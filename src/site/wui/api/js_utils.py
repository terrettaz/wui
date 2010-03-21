import os

from pprint import pprint

class JSParser():
    
    comment_start = '/**'
    comment_end = '*/'
    
    def __init__(self, path):
        self.path = path
        self.token_looked = None
    
    def parse(self):
        if not os.path.exists(self.path):
            raise Exception('file "%s" not found' % self.path)
        
        self.file = open(self.path)
        self.comments = []
        while True:
            comment = self.next_comment()
            if not comment:
                break
            self.comments.append(comment)
    
    def build_documentation(self):
        documentation = {
            'ns':{},
            'classes':{},
            'functions':{},
        }
        
        current_ns = None
        current_class = None
        for comment in self.comments:
            
            if comment['namespace'] != None:
                if not current_ns:
                    current_ns = comment
                    documentation['ns'][current_ns['namespace']] = current_ns
                elif comment['namespace'] != current_ns['namespace']:
                    current_ns = None
                    current_class = None

            elif comment['class'] != None:
                if not current_class or comment['class'] != current_class['class']:
                    current_class = comment
                if current_ns:
                    classes = current_ns.get('classes', {})
                    current_ns['classes'] = classes
                else:
                    classes = documentation['classes']
                classes[current_class['class']] = current_class

            elif current_class and comment['constructor'] != None:
                constructors = current_ns.get('constructors', [])
                current_class['constructors'] = constructors
                constructors.append(comment)
            
            elif current_class and comment['method'] != None:
                methods = current_ns.get('methods', [])
                current_class['methods'] = methods
                methods.append(comment)
                
            elif current_class and comment['function'] != None:
                documentations.append(comment)
        
        return documentation
        
    def next_token(self):
        if self.token_looked:
            t = self.token_looked
            self.token_looked = None
            return t
        token = ''
        white_chars = ''
        while True:
            ch = self.next_char()
            if ch == 'EOF':
                token = None
                break
            elif token == '' and ch in '\r\n\t \n':
                white_chars += ch
            elif token != '' and ch in '\r\n\t \n':
                break
            else:
                token += ch
        return token
    
    def look_token_ahead(self):
        self.token_looked = self.next_token()
        return self.token_looked
    
    def next_char(self):
        ch = self.file.read(1)
        if not ch:
            ch = 'EOF'
        return ch
    
    # returns
    def next_comment(self):
        in_comment = False
        comment = {
            'comment':'',
            'author':'',
            'namespace':None,
            'class':None,
            'constructor':None,
            'method':None,
            'function':None,
            'parameters':[],
            'options':[],
            'return':None,
            'notice':None,
            'super':None,
        }
        
        buff = ''
        while True:
            token = self.next_token()
            if not in_comment and token == JSParser.comment_start:
                in_comment = True
                continue
            elif token == JSParser.comment_end:
                in_comment = False
                break
            else:
                if not token:
                    return False;
                    
            if in_comment:
                if token == '*':
                    if comment['comment'] != '':
                        comment['comment'] += '\n'
                elif token in ['@author', '@namespace', '@class', '@method', '@constructor', '@return', '@super', '@notice', '@function']:
                    comment[token[1:]] = self.next_comment_part(token)
                elif token in ['@parameter', '@param', '@params']:
                    comment['parameters'].append(self.next_comment_part(token))
                elif token in ['@option', '@options']:
                    comment['options'].append(self.next_comment_part(token))
                else:
                    comment['comment'] += token + ' '
        
        return comment
    
    def next_comment_part(self, token):
        comment = ''
        while True:
            token_ahead = self.look_token_ahead()
            if token_ahead.startswith('@') or token_ahead == JSParser.comment_end:
                break
            token = self.next_token()
            if token == '*':
                if comment != '':
                    comment += '\n'
            else:
                comment += token + ' '
        
        return comment.strip()

def create_documentation(js_file):
    parser = JSParser(js_file)
    parser.parse()
    return parser.build_documentation()