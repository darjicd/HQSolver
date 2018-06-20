from config import readFromConfig
from solvers.naive import Naive
from solvers.gsearch import Google
from solvers.wiki import Wikipedia

from queue import Queue
from shutil import get_terminal_size
from threading import Thread


class Solver(object):
    def __init__(self):
        self.debug = readFromConfig("General", "debug_mode")
        self.google_api_key = readFromConfig("Solver", "google_api_key")
        self.google_cse_id = readFromConfig("Solver", "google_cse_id")
        self.show_advancing_players = readFromConfig("Solver", "show_advancing_players")
        self.show_answers = readFromConfig("Solver", "show_answers")
        self.show_answerids = readFromConfig("Solver", "show_answerids")
        self.show_category = readFromConfig("Solver", "show_category")
        self.show_eliminated_players = readFromConfig("Solver", "show_eliminated_players")
        self.show_summary = readFromConfig("Solver", "show_summary")
        self.show_players_answers = readFromConfig("Solver", "show_players_answers")
        self.show_solver_summary = readFromConfig("Solver", "show_solver_summary")
        self.show_question = readFromConfig("Solver", "show_question")
        self.show_questionid = readFromConfig("Solver", "show_questionid")
        self.show_question_count = readFromConfig("Solver", "show_question_count")
        self.show_question_number = readFromConfig("Solver", "show_question_number")
        self.use_naive = readFromConfig("Solver", 'use_naive')
        self.use_google = readFromConfig("Solver", "use_google")
        self.use_wiki = readFromConfig("Solver", "use_wiki")

        if self.use_naive:
            self.naive = Naive(self.google_api_key, self.google_cse_id, self.debug)
        if self.use_google:
            self.google = Google(self.debug)
        if self.use_wiki:
            self.wiki = Wikipedia(self.debug)

    def solve(self, message):
        self.question = message

        if self.question["type"] == "question":
            self.showQuestion()

            answers = self.question["answers"]
            category = self.question["category"]
            question = self.question["question"]

            print(" Solvers ".center(get_terminal_size()[0], "="))
            print()

            solverThreads = []

            queue = Queue()

            if self.use_naive:
                naiveThread = Thread(target=self.naive.solve, args=(question, answers, queue))
                naiveThread.start()
                solverThreads.append(naiveThread)

            if self.use_wiki:
                wikiThread = Thread(target=self.wiki.solve, args=(question, answers, category, queue))
                wikiThread.start()
                solverThreads.append(wikiThread)

            if self.use_google:
                googleThread = Thread(target=self.google.solve, args=(question, answers, queue))
                googleThread.start()
                solverThreads.append(googleThread)

            # Join all the threads
            for thread in solverThreads:
                thread.join()

            predictions = []
            while not queue.empty():
                predictions.append(queue.get())

            answerCount = [0, 0, 0]

            for prediction in range(len(predictions)):
                answerCount[0] = answerCount[0] + predictions[prediction][0]
                answerCount[1] = answerCount[1] + predictions[prediction][1]
                answerCount[2] = answerCount[2] + predictions[prediction][2]

            total = answerCount[0] + answerCount[1] + answerCount[2]

            if self.show_solver_summary:
                print()
                print(" Solver Summary ".center(get_terminal_size()[0], "="))

                for answer in range(len(answers)):
                    if answerCount[answer] == 0:
                        percent = 0
                    else:
                        percent = round((answerCount[answer] / total) * 100, 2)

                    print((answers[answer]['text'] + " (Probability: " + str(percent) + "%)").center(get_terminal_size()[0]))

            print()
            if answerCount.count(0) == 3:
                print(" None of the solvers gave an answer! ".center(get_terminal_size()[0], "*"))
            else:
                mostPropably = answerCount.index(max(answerCount))
                percent = round((max(answerCount) / total) * 100, 2)
                answer = answers[mostPropably]['text']

                print((" The most probable answer is: \33[34m" + answer + "\33[0m (Probability: " + str(percent) + "%)").center(get_terminal_size()[0], "*"))

            print("".center(get_terminal_size()[0], "="))
        elif self.question["type"] == "questionSummary" and self.show_summary:
            self.showSummary()
        return True

    def showQuestion(self):
        print(" Question ".center(get_terminal_size()[0], "="))
        print()

        if self.show_question_count or self.show_question_number:
            tempPrint = ""
            if self.show_question_count:
                tempPrint += "Question " + str(self.question["questionNumber"])
            if self.show_question_count and self.show_question_number:
                tempPrint += "/" + str(self.question["questionCount"])
            elif self.show_question_number:
                tempPrint += "Questions: " + str(self.question["questionCount"])

            print(tempPrint.center(get_terminal_size()[0]))

        if self.show_category:
            print(("Category: " + str(self.question["category"])).rjust(get_terminal_size()[0]))
            print()

        if self.show_question or self.show_questionid:
            tempPrint = ""
            if self.show_question:
                tempPrint += self.question["question"].encode( "UTF-8" ) 
            if self.show_question:
                tempPrint += " (" + str(self.question["questionId"]) + ")"
            elif self.show_questionid:
                tempPrint += str(self.question["questionId"])

            print(tempPrint.center(get_terminal_size()[0]))

        if self.show_answers or self.show_answerids:
            answers = self.question["answers"]
            answersCount = len(answers)

            for answer in range(answersCount):
                tempPrint = ""

                if self.show_answers:
                    tempPrint += str(answers[answer]["text"])
                if self.show_answers and self.show_answerids:
                    tempPrint += " (" + str(answers[answer]["answerId"]) + ")"
                elif self.show_answerids:
                    tempPrint += str(answers[answer]["answerId"])

                print()
                print(tempPrint.center(get_terminal_size()[0]))

        print("".center(get_terminal_size()[0], "="))
        return True

    def showSummary(self):
        print(" Question Summary ".center(get_terminal_size()[0], "="))
        print()

        if self.show_question or self.show_questionid:
            tempPrint = ""
            if self.show_question:
                tempPrint += str(self.question["question"])
            if self.show_question and self.show_questionid:
                tempPrint += " (" + str(self.question["questionId"]) + ")"
            elif self.show_questionid:
                tempPrint += str(self.question["questionId"])
            print(tempPrint.center(get_terminal_size()[0]))
            print()

        if self.show_answers or self.show_answerids or self.show_players_answers:
            answers = self.question["answerCounts"]
            answersCount = len(answers)

            for answer in range(answersCount):
                tempPrint = ""

                answerId = str(answers[answer]["answerId"])
                answerText = str(answers[answer]["answer"])
                isCorrect = answers[answer]["correct"]
                count = str(answers[answer]["count"])

                if isCorrect:
                    tempPrint += "\33[32m"
                else:
                    tempPrint += "\033[91m"

                if self.show_answers:
                    tempPrint += answerText
                if self.show_answers and self.show_answerids:
                    tempPrint += " (" + answerId + ")"
                elif self.show_answerids:
                    tempPrint += answerId

                tempPrint += "\33[0m"

                print(tempPrint.center(get_terminal_size()[0]))

                if self.show_players_answers:
                    print(("Players who marked this answer: " + count).center(get_terminal_size()[0]))
                print()

            if self.show_advancing_players:
                print(("Advancing Players: " + str(self.question["advancingPlayersCount"])).center(
                    get_terminal_size()[0]))
            if self.show_eliminated_players:
                print(("Eliminated Players: " + str(self.question["eliminatedPlayersCount"])).center(
                    get_terminal_size()[0]))

            print("".center(get_terminal_size()[0], "="))
        return True
