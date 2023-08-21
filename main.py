#coding=utf-8

from scanner import Scanner
from syntax_parser import SyntaxAnalyzer
from checker import ASTChecker

if __name__ == "__main__":
	sc = Scanner()
	parser = SyntaxAnalyzer()
	checker = ASTChecker()
	text = '''void main();
int x = 0;
int y = 1;
int z = 2;

void main(int argc)
{ 
	z = 1;
	y = argc + z;
	1 = z;
}
    '''
	#sc.run(text)
	tokens = sc.parse(text)
	result = parser.parse(tokens)
	checker.check(result)
	pass