from DNS_Message_Header import MessageHeader
from DNS_Question import DNSQuestion
from DNS_Answer import Answer


class MessageFormat:
    def __init__(self, q_type, host_name):
        self.host_name = host_name
        self.q_type = q_type
        self.header = MessageHeader()
        self.questions = []
        self.answers = []
        self.authority_rrs = []
        self.additional_rrs = []

    def encode_message(self):
        message = b''
        message += self.header.encode_header()

        question = DNSQuestion(self.q_type, self.host_name)
        message += question.encode_question()
        return message

    def decode_message(self, message):
        self.header.decode_header(message)
        offset = self.header.length

        for i in range(self.header.questions_count):
            self.questions.append(DNSQuestion(self.q_type, self.host_name))
            offset = self.questions[i].decode_question(message, offset)

        for i in range(self.header.answers_count):
            self.answers.append(Answer())
            offset = self.answers[i].decode_info(message, offset)

        for i in range(self.header.access_rights_count):
            self.authority_rrs.append(Answer())
            offset = self.authority_rrs[i].decode_info(message, offset)

        for i in range(self.header.additional_info_count):
            self.additional_rrs.append(Answer())
            offset = self.additional_rrs[i].decode_info(message, offset)

    def print_result(self, debug):
        results = []
        answers = []
        name_servers = []
        additional_answers = []

        print('DATA:')
        self.header.print_data()
        print()

        for i in range(len(self.questions)):
            print('QUESTION {0}:'.format(i + 1))
            self.questions[i].print_question(debug)
            print()

        for i in range(len(self.answers)):
            print('ANSWER {0}:'.format(i + 1))
            answers.append(self.answers[i].print_answer(debug))
            print()

        for i in range(len(self.authority_rrs)):
            print('AUTHORITY ANSWER {0}:'.format(i + 1))
            name_servers.append(self.authority_rrs[i].print_answer(debug))
            print()

        for i in range(len(self.additional_rrs)):
            print('ADDITIONAL ANSWER {0}:'.format(i + 1))
            additional_answers.append(self.additional_rrs[i].print_answer(debug))
            print()

        answers.extend(additional_answers)
        results.append(answers)
        results.append(name_servers)
        print(f'Answers: {answers}')
        print(f'Authority answers: {name_servers}')
        print(f'Additional answers: {additional_answers}\n')
        return results
