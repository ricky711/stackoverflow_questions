# stackoverflow_questions
对stackoverflow.com的question页面，按votes倒序排序，爬前面主要的问题。

数据获取：

主要采用爬取器+解析器+存储器+调度器的结构，主要用函数的形式实现，没有进行完整的封装。

1. requests进行网页爬取，并利用HttpAdapter设置retry次数；
2. 美丽汤BeautifulSoup进行页面解析；
3. mysql进行数据存储，pymysql进行连接；
4. 尝试用multiprocessing进行多线程执行，Process()开线程，Manager().Queue()进行线程间信息同步（待爬任务队列，失败任务队列）。

尝试过用multiprocessing.Pool，然而写入mysql时不知道为啥出现数据丢失的情况（一脸懵逼），特别线程开的越多丢失越严重，这个需要后面再慢慢研究原因，是多线程同时写入数据库导致的问题还是啥？？？

更新，见crawl_2.py：
1. 开两个Manager().Queue()队列，一个用于存放待爬取目标，一个存放待存储目标；
2. 爬取与存储分开任务，先开多个线程完成爬取任务，把待存储目标存放与队列中，再开多线程进行数据存储；
3. 改写main函数，拆分成两个调度函数，一个爬取调度，一个存储调度；
4. 优化storage()函数，原来一条一条数据进行execute+commit，改成executemany批量添加后再commit
5. 后续需要优化的地方：爬取任务与存储任务同时执行，爬取任务进行过程中，只要存储队列中有数据就进行存储。

更新：

嗯~ o(*￣▽￣*)o。。原来写入mysql数据丢失的问题不是因为进程的问题。。而是parser()函数进行解析的时候没有考虑到网页内容异常的情况，导致没有解析到目标内容，函数返回就是个[]，导致写入失败。。所以异常检测还是不能偷懒不码的。。

加入了多个检测添加，终于发现访问频繁response会提示，

<h1>Too many requests</h1>\n 
    <p>This IP address () has performed an unusual high number of requests and has been temporarily rate limited. If you believe this to be in error, please contact us at <a href="mailto:team@stackexchange.com?

不过趁这个机会尝试了使用multiprocess.Manager().Queue()进行消息同步，还有Process()的使用

数据分析：

tbc...

