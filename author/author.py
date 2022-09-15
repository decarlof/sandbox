
import re

filename  = '/Users/decarlo/conda/sandbox/author/APS-publications-2017-2020.txt'
# xsd_authors = ['D. Shu', 'Parab', 'Cang Zhao', 'Antonino Miceli', 'Deming Shu', 'Joseph Sullivan', 'Lahsen Assoufid', 'Mathew Cherukara', 'Mike Fisher', 'Nicholas Schwarz', 'Anthony Krzysko', 'John Weizeorick', 'Lisa Gades', 'Mike Hammer', 'Orlando Quaranta', 'Tejas Guruswamy', 'Umeshkumar Patel', 'Dennis Trujillo', 'Evan Maxey', 'Fabricio Marin', 'Jeffrey Klug', 'Jörg Maser', 'Junjing Deng', 'Lu Xi Li', 'Michael Bartlein', 'Olga Antipova', 'Ross Harder', 'Si Chen', 'Volker Rose', 'Wonsuk Cha', 'Yi Jiang', 'Zhonghou Cai', 'Yanqi Luo', 'Alexis Quental', 'Benjamin Reinhart', 'Charles Kurtz', 'Ivan Kuzmenko', 'Jan Ilavsky', 'Randall Winans', 'Soenke Seifert', 'Sungsik Lee', 'Xiaobing Zuo', 'Inhui Hwang', 'Chris Benmore', 'David Gagliano', 'Douglas Robinson', 'Fanny Rodolakis', 'Gilberto Fabbris', 'Jessica McChesney', 'Joerg Strempfer', 'John Freeland', 'Jong Woo Kim', 'Matthew Krogstad', 'Michael McDowell', 'Philip Ryan', 'Yongseong Choi', 'Zahir Islam', 'Matthew Highland', 'Robert Winarski', 'Matt Frith', 'Steven Kearney', 'Jayson Anton', 'Sheikh Mashrafi', 'Alan Kastengren', 'Alex Deriy', 'Kamel Fezzaa', 'Pavel Shevchenko', 'Samuel Clark', 'Viktor Nikitin', 'Yuelin Li', 'David Cyl', 'Dina Sheyfer', 'Evguenia Karapetrova', 'Hawoong Hong', 'Hua Zhou', 'Wenjun Liu', 'Zhan Zhang', 'Ali Mashayekhi', 'Andrew Chuang', 'John Okasinski', 'Jun-Sang Park', 'Peter Kenesei', 'Sarvjit Shastri', 'Byeongdu Lee', 'Uta Ruett', 'Xiaoyi Zhang', 'Alec Sandy', 'Andrzej Joachimiak', 'Dean Haeffner', 'Maddury Somayazulu', 'Stefan Vogt', 'Jeff Kirchman', 'Keenan Lang', 'Kevin Peterson', 'Kurt Goetze', 'Mark Engbretson', 'Max Wyman', 'Pete Jemian', 'Roy Ignacia Guerra', 'Shefali Saxena', 'Thomas Walsh', 'Tim Mooney', 'Brandon Stone', 'Jun Qian', 'Luca Rebuffi', 'Michael Wojcik', 'Raymond Conley', 'Xianbo Shi', 'XianRong Huang', 'Yury Shvydko', 'Elina Kasman', 'Paresh Pradhan', 'Arun Bommannavar', 'Changyong Park', 'Curtis Kenney-Benson', 'Dmitry Popov', 'Eric Rod', 'Guoyin Shen', 'Jesse Smith', 'Paul Chow', 'Richard Ferry', 'Ross Hrubiak', 'Yue Meng', 'Yuming Xiao', 'Dean Smith', 'Mingda Lyu', 'Ashish Tripathi', 'Brian Toby', 'Doga Gursoy', 'Hemant Sharma', 'Michel Van Veenendaal', 'Daniel Ching', 'Yudong Yao', 'Anakha V Babu', 'Saugat Kandel', 'Altaf Khan', 'Andrew Bernhard', 'Curt Preissner', 'Dana Capatina', 'Erika Benda', 'Gary Navrotski', 'Jonathan Knopp', 'Kevin Wakefield', 'Sunil Bean', 'Timothy Bender', 'Benjamin Davis', 'Joanna Tan', 'Arthur Glowacki', 'Barbara Frosik', 'Faisal Khan', 'Hannah Parraga', 'John Hammonds', 'Ke Yue', 'Miaoqi Chu', 'Sinisa Veseli', 'Steven Henke', 'Howard Yanxon', 'Jiahui Chen', 'Bing Shi', 'Dale Ferguson', 'Shenglan Xu', 'Stephen Corcoran', 'Craig Ogata', 'David Kissick', 'Michael Becker', 'Nagarajan Venugopalan', 'Sergey Stepanov', 'Mark Hilgart', 'Oleg Makarov', 'Qingping Xu', 'Chengjun Sun', 'George Sterbinsky', 'Michael Pape', 'Steve Heald', 'Tianpin Wu', 'Barry Lai', 'Daniel Haskel', 'Francesco De Carlo', 'Jon Tischler', 'Jonathan Almer', 'Robert Fischetti', 'Shelly Kelly', 'Suresh Narayanan', 'Thomas Gog', 'Eric Dufresne', 'Joe Strzalka', 'Qingteng Zhang', 'Raymond Ziegler', 'Zhang Jiang', 'Ahmet Alatas', 'Ayman Said', 'Diego Casa', 'Emily Aran', 'Esen Alp', 'Jiyong Zhao', 'Jung Ho Kim', 'Mary Upton', 'Michael Hu', 'Rick Krakora', 'Thomas Toellner', 'Andrey Yakovenko', 'Guy Jennings', 'Kamila Wiaderek', 'Kevin Beyer', 'Leighanne Gallington', 'Lynn Ribaud', 'Olaf Borkiewicz', 'Saul Lapidus', 'Wenqian Xu', 'Tiffany Kinnibrugh', 'Harry Charalambous', 'Tianyi Li', 'Zhi Qiao', 'Burak Guzelturk', 'Eli Kinigstein', 'Don Jensen', 'Donald Walko', 'Jin Wang', 'Richard Spence', 'Faran Zhou', 'Jin Yu', 'Jinxing Jiang', 'Marc Zajac', 'Qing Zhang', 'Peco Myint']
# # # xsd_authors = ['Qingteng Zhang','Q. Zhang']
# # xsd_authors = ['Deming Shu','D. Shu']
# # xsd_authors = ['Xianbo Shi', 'X. Shi']
# # # xsd_authors = ['Y. Yao','Yudong Yao',]
# # # xsd_authors = ['Guoyin Shen', 'G. Shen']
# # # xsd_authors = ['Tianyi Li', 'T. Li', 'Li Tianyi']
# # # xsd_authors = ['Zhi Qiao', 'Qiao']
# # # xsd_authors = ['Byeongdu Lee', 'B. Lee']
# # # xsd_authors = ['Junjing Deng','J. Deng']
xsd_authors = ['Nikitin', 'De Carlo', 'Parab', 'Cang Zhao', 'Tao Sun', 'Fezzaa', 'Kastengren', 'Xianghui Xiao', 'Xiaogang Yang', 'Prabat', 'Soriano']

count = 0 
file = open(filename,'r')
while True:
    next_line = file.readline()

    if not next_line:
        break;
    if next_line != '\n':
        first_author = next_line.strip().split(",")[0]
        for author in xsd_authors:
            if re.search(r"\b" + re.escape(author) + r"\b", first_author):
                count+=1
                print(first_author, next_line.strip().split(",")[-1])

file.close()

print(count)