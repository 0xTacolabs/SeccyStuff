#!/usr/bin/python


import re
import sys
#open the file for converting
#Will upgrade to use argparse eventually


filename = sys.argv[1]

file = open(filename, "r")
lines = file.readlines()
normalised = ""
varDict = {}

def removeUnicode(line):
        #removes basic unicode encodings
        try:
            #basic regex search for unicode
            p = re.compile(r'\\u\d\d[\d\w]{2}')
            results = p.findall(line)
            #search and replace unicode with ascii representation
            for i in results:
                num = i[2:]
                line = line.replace(i,chr(int(num,16)))

        except:
            pass

        return line

def beautify(text):
    #beautifies text, slightly
    #probably needs some work
    normalised = text.strip()
    normalised = normalised.replace("[{", "[\n{")
    normalised = normalised.replace("= =", "==")
    normalised = normalised.replace("{", "{\n\t")
    normalised = normalised.replace("}", "\n}")
    normalised = normalised.replace("}+", "\n+\n")
    #normalised = normalised.replace("= =", "==")
    
    return normalised

for section in lines:
    section = section.split(";")
    for line in section:
        normalised += removeUnicode(line) + ";\n"

normalised = normalised.strip()

processed = ""
varValue = ""
secVarName = ""
varName = ""
valid_chars = "\w\d\_\.\-\+\/\'\"\\\?\%"
var_type = ""
valid_math = "\d\*\-\+"

def OneLiner(line):
        #checks if variable/function is declared over a single line
    try:
        p = re.compile(r'^(var\s+)?[\w\d]+\s*=[\w\+\s\d\'\.]+;$')
        r = p.search(line)
        if r:
            return True
    except:
        pass
    return False


def isMath(line):
    
    #checks if any mathematic equations are within the given line
    math = re.compile(r'(\(['+valid_math+']+\))')
    results = math.search(line)
    if results:
        return True
    else:
        return False

def evaluateMath(line):
    #evaluate any math found in isMath function
    #could probably be combined into one function is try/except is used
    try:
        math = re.compile(r'(\(['+valid_math+']+\))')
        results = math.findall(line)
        for i in results:
            line = line.replace(i,"("+str(eval(i))+")")
    except Exception as e:
        print("Math Evaluation Failed: "+i)
        print(e)
        pass
    return line


def obArray(line):
    """determines whether an array has been obfuscated using the "{tu0:'a'}.tu0" style"""
    getVar = re.compile(r'\{([\d\w]+)\:[\'\"]([\d\w]+)[\'\"]\}')
    results = getVar.search(line)
    if results:
        return True
    return False

def remove_ob_array(line):
        """deals with arrays that have been obfuscated using "{tu0:'a'}.tu0" style"""
        
        getVar = re.compile(r'(\{([\d\w]+)' + '\:[\'\"]' + '([\d\w\:\.\/\?\=\ \&\%]+)' + '[\'\"]\})')
        res = getVar.findall(line)

        #assigns captured values to variables for search/replace function
        for tup in res:
            full = tup[0]
            key = tup[1]
            char = tup[2]
            line = re.sub(full+'\.'+key+'\s*\+?\s*',char,line)
        return line

def resolveVars(line, varDict):
    """resolves variable names if already defined on previous line
        eg deals with 
            var AAA3 = "activeXobject";
            var BBB3 = new AAA3;
        (in above example, AAA3 will be replaced with "activeXobject")

    """
    #regex searches for all possible "words" within the given line
    d = re.compile(r'([\w\d]+)+')
    results = d.findall(line)

    #replace any found word with its previous declared value
    for i in results:
        if i in varDict.keys():
            line = re.sub(i,varDict[i], line)

    return line,varDict


def updateDict(var,value,varDict):
        #replace vars with previously defined variables
        value,varDict = resolveVars(value,varDict)
        #remove accidentally captured brackets
        value = value.strip("[]")
        if var in varDict.keys():
            var = varDict[var]
        elif var not in varDict.keys():
            varDict[var] = value

        return varDict

        
def updateLine(line,varDict):
    #makes sure that only the right hand side gets updated
    #resolves variable/function names to previously defined values

    if ("=" in line):
        rsideStart = line.index('=')
        rside = line[rsideStart:]

    else:
        rside = line

    d = re.compile(r'([\w\d]+)+')
    results = d.findall(rside)

    for i in results:
        if i in varDict.keys():
            line  = re.sub(i,varDict[i], line)
    return line


def extractVars(line,varDict):

    line = line.strip()
    #Pretty gross regex for extracting variable/function declarations
    #Boldly assumes taht function will all be on one line
    c = re.compile('^(var\s*)?' + '([\d\w\_\-]+)' + '\s*=\s*' + '(this|new)?\s*' + '([\w\d\.\(\[\)\]]+)' + '\s*;$')
    s = c.findall(line)

    line = updateLine(line,varDict)
    if s:
        s = s[0]
        var_name = s[1]
        varValue = s[-1]
        varDict = updateDict(var_name,varValue,varDict)

    return (line,varDict)

#####################################################33

def main():
    processed = ""
    varDict = {}

    for line in normalised.split("\n"):
        #leave line as is?
        #if (OneLiner(line)):
        #   line = line
        #print(line)
        #resolves mathematical equations used to obfuscate
        #eg resolves "namespace(15-8)" to "namespace(7)"
        if isMath(line):
            line = evaluateMath(line)
        if obArray(line):
            line = remove_ob_array(line)
            #print(line)
        if line:
                processed += line.strip()+'\n'

        #normalisation is done?
        # now time to build a dictionary?

    for line in processed.split("\n"):
        try:
            line,varDict = extractVars(line,varDict)
        except Exception as e:
                print(e)
        #print(beautify(line))
        print(line)
    print(varDict)
        
    return 0    



##############################################################
if __name__ == "__main__":
    main()
