# stackoverflow_questions
对stackoverflow.com的question页面，按votes倒序排序，爬前面主要的问题。

数据获取：

主要采用爬取器+解析器+存储器+调度器的结构，主要用函数的形式实现，没有进行完整的封装。

1. requests进行网页爬取，并利用HttpAdapter设置retry次数；
2. 美丽汤BeautifulSoup进行页面解析；
3. mysql进行数据存储，pymysql进行连接；
4. 尝试用multiprocessing进行多线程执行，Process()开线程，Manager().Queue()进行线程间信息同步（待爬任务队列，失败任务队列）。

尝试过用multiprocessing.Pool，然而写入mysql时不知道为啥出现数据丢失的情况（一脸懵逼），特别线程开的越多丢失越严重，这个需要后面再慢慢研究原因，是多线程同时写入数据库导致的问题还是啥？？？


数据分析：

tbc...

