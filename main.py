#coding=utf-8

from scanner import Scanner
from syntax_parser import SyntaxAnalyzer

if __name__ == "__main__":
    sc = Scanner()
    parser = SyntaxAnalyzer()

    text = '''void main()
{ 
	int a[][] = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};
    func(a[x][y]);
    return a[1][2];
}
    '''
    #sc.run(text)
    tokens = sc.parse(text)
    result = parser.parse(tokens)
    print(result)