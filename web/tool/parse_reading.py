import os
import glob
import re

_DEFAULT_EXAM_FOLDER = "../exams"

_SPECIAL_ = {"\\uc0\\u9675": "",
             "\\uc0\\u9608": "<BLOCK>",
             "\\ul": "<b q=\"\">",
             "\\ulnone": "</b>",
             "\\cb2": "<hl>",
             "\\cb1": "</hl>",
             "\\'92": "'",
             "\\'93": ' \"',
             "\\'94": '\" ',
             "\\'97": "--"}


class ParseReading:
    def splitBy(self, data, regex):
        list = []
        part = []
        for line in data:
            if re.match(regex,line):
                if len(part) > 0:
                    list.append(part)
                    part = []
            part.append(line)
        if len(part) > 0:
            list.append(part)
        return list

    def forwardUlnone(self, line):
        for m in re.finditer("ulnone", line):
            left = line[:m.start() - 1]
            right = line[m.start() - 1:]

            for key in _SPECIAL_:
                while left.endswith(" "):
                    left = left[:-1]
                if left.endswith(key):
                    line = left[::-1].replace(key[::-1], "\\ulnone"[::-1], 1)[::-1] + \
                           right.replace("\\ulnone", key, 1)
        return line

    def getInitIndex(self, line):
        parts = line.split(":")
        if re.match("[0-9][0-9]?", parts[0]):
            return int(parts[0]), parts[1].strip()

    # filter some unnecessary chars and prepare for parsing
    def prepare(self, data):
        new_data = []
        for line in data:
            line = self.forwardUlnone(line)

            if line.startswith("{\\") or len(line) == 0:
                continue
            for key in _SPECIAL_:
                if key in line:
                    line = line.replace(key, _SPECIAL_[key])

            words = line.split(" ")
            new_line = ""
            for word in words:
                if word.startswith("\\"):
                    continue
                if len(word) != 0:
                    new_line += " " + word
            new_line = new_line.strip()
            if len(new_line) == 0:
                continue

            # new_line = new_line[:-1]
            new_data.append(new_line)
        return new_data

    # Generate content
    def genObject(self, data):
        paragraphs = []
        questions = []
        question_to_paragraph = []
        question_points = []
        title = data[1]
        for index in range(2, len(data)):
            if data[index].startswith("Paragraph 1:"):
                break
            paragraphs.append(data[index])
        parts = self.splitBy(data[index:], r"Paragraph .*")

        index = 0
        for part in parts:
            i = 0
            for line in part:
                if line.startswith("Paragraph"):
                    index, content = self.getInitIndex(line.replace("Paragraph ", "", 1))
                    paragraphs[index - 1] = content
                else:
                    break
                i += 1

            list = self.splitBy(part[i:], r"[0-9][0-9]?.*")
            for question in list:
                point = 1
                for line in question:
                    words = line.split(" ")
                    for j in range(1, len(words) - 1):
                        if words[j + 1] == "points":
                            point = int(words[i])
                            break
                question_points.append(point)
                questions.append(question)
                question_to_paragraph.append(index)
        self.genJson(title, paragraphs, questions, question_to_paragraph, question_points)

    # Generate json
    def genJson(self, title, paragraphs, questions, question_to_paragraph, question_points):
        json = ""
        json += "{\n"
        json += "\t\"title\": \"%s\",\n" % title
        json += "\t\"image\": \"\",\n"
        json += "\t\"paragraphs\": [\n"
        for line in paragraphs:
            json += "\t\t\"%s\",\n" % line
        json += "\t],\n"

        json += "\t\"question\": [\n"
        index = 0
        for line in questions:
            json += "\t\t{\n"
            json += "\t\t\t\"type\": \"\",\n"
            json += "\t\t\t\"paragraph\": %d,\n" % question_to_paragraph[index]
            json += "\t\t\t\"point\": %d,\n" % question_points[index]
            json += "\t\t\t\"description\": \"%s\",\n" % line[0]
            json += "\t\t\t\"option\": [\n"
            for i in range(1, len(line)):
                json += "\t\t\t\t\"%s\",\n" % line[i]
            json += "\t\t\t],\n"
            json += "\t\t\t\"answer\" : 0,\n"
            json += "\t\t},\n"
            index += 1
        json += "\t],\n"
        json += "}"

        print json

    def parse(self):
        os.chdir(_DEFAULT_EXAM_FOLDER)
        files = glob.glob("reading_1.rtf")
        for filename in files:
            print "Open %s" % filename
            with open(filename) as file:
                data = file.readlines()
                data = self.prepare(data)
                self.genObject(data)

