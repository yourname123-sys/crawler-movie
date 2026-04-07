import  requests
import csv
from lxml import html

TMDB_BASE_URL="https://www.themoviedb.org"
TMDB_URL_1 = "https://www.themoviedb.org/movie/top-rated"  #高分电影榜单的url(第1页)
TMDB_URL_2 = "https://www.themoviedb.org/discover/movie/items" #高分电影榜单的url(第2页之后)

MOVIE_LIST_FILE="CSV_data/movie.csv"

#获取电影名，年份，上映时间，类型，时长，评分，语言，导演，作者，主演，slogan，简介
def get_movie_info(movie_url):    #获取电影详情数据函数
    movie_response = requests.get(movie_url, timeout=60)  # 发送请求，获取数据
    movie_doc = html.fromstring(movie_response.text)  # 解析response，解析成文档对象
    print(f"发送请求{movie_url}，获取电影详情数据...")

    movie_names = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/h2/a/text()") #获取电影名
    movie_years = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/h2/span/text()")  # 获取电影年份

    movie_dates = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/div/span[@class='release']/text()")  # 获取电影上映时间
    movie_types = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/div/span[@class='genres']/a/text()")  # 获取电影类型
    movie_cost_times = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/div/span[@class='runtime']/text()")  # 获取电影时长

    movie_scores = movie_doc.xpath("//*[@id='consensus_pill']/div/div[1]/div/div/@data-percent")  # 获取电影评分
    movie_languages = movie_doc.xpath("//*[@id='media_v4']/div/div/div[2]/div/section/div[1]/div/section[1]/p[3]/text()")  # 获取电影语言
    movie_directors = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[3]/ol/li[1]/p[1]/a/text()")  # 获取电影导演
    movie_aouthors = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[3]/ol/li[2]/p[1]/a/text()")  # 获取电影作者

    movie_starring = movie_doc.xpath("//*[@id='cast_scroller']/ol/li[1]/p[1]/a/text()") #获取电影主演

    movie_slogan = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[3]/h3[1]/text()") #获取电影slogan

    movie_introductions = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[3]/div/p/text()")  # 获取电影简介
    #返回电影数据 - 字典
    movie_info = {
        "电影名": movie_names[0].strip() if movie_names else "",
        "电影年份": movie_years[0].strip() if movie_years else "",
        "上映时间": movie_dates[0].strip() if movie_dates else "",
        "类型": ",".join(movie_types) if movie_types else "",
        "时长": movie_cost_times[0].strip() if movie_cost_times else "",
        "评分": movie_scores[0].strip() if movie_scores else "",
        "语言": movie_languages[0].strip() if movie_languages else "",
        "导演": ",".join(movie_directors) if movie_directors else "",
        "作者": ",".join(movie_aouthors) if movie_aouthors else "",
        "主演": movie_starring[0].strip() if movie_starring else "",
        "宣传语": movie_slogan[0].strip() if movie_slogan else "",
        "简介": movie_introductions[0].strip() if movie_introductions else ""
    }   #strip()作用是去除字符串首尾的空格
    return movie_info





def save_movie(all_movie):   #保存电影数据函数
        with open(MOVIE_LIST_FILE, "w", encoding="utf-8", newline="") as csvfile:  #newline=""作用是去掉csv文件中的\n
            writer = csv.DictWriter(csvfile, fieldnames=["电影名", "电影年份", "上映时间", "类型", "时长", "评分", "语言", "导演", "作者", "主演", "宣传语", "简介"])
            writer.writeheader() #writeheader方法作用是写入表头
            writer.writerows(all_movie) #写入数据


def main():
    all_movie = []  # 创建一个空列表，用于存储所有电影数据

    #循环获取电影列表，从1到5页
    for page_num in range(1, 6):
        # 发送请求，获取高分电影榜单数据
        if page_num==1:
                 response = requests.get(TMDB_URL_1, timeout=60)  # 发送请求，获取数据，timeout参数作用是设置请求超时时间，超过这个时间就返回错误
        else:
                 response = requests.post(TMDB_URL_2,
                                          data=f"air_date.gte=&air_date.lte=&certification=&certification_country=CN&debug=&first_air_date.gte=&first_air_date.lte=&include_adult=false&latest_ceremony.gte=&latest_ceremony.lte=&page={page_num}&primary_release_date.gte=&primary_release_date.lte=&region=&release_date.gte=&release_date.lte=2026-09-13&show_me=everything&sort_by=vote_average.desc&vote_average.gte=0&vote_average.lte=10&vote_count.gte=300&watch_region=CN&with_genres=&with_keywords=&with_networks=&with_origin_country=&with_original_language=&with_watch_monetization_types=&with_watch_providers=&with_release_type=&with_runtime.gte=0&with_runtime.lte=400",
                                          timeout=60)   #data为请求体，请求体作用是发送数据给服务器
        print("发送请求，获取高分电影榜单数据...")

        # 解析数据，获取电影列表
        document = html.fromstring(response.text)  # 解析response，解析成文档对象
        data_list = document.xpath(
            f"//*[@id='page_{page_num}']/div[@class='card style_1']")

        # 遍历电影列表获取电影详情

        for movie in data_list:
            movie_urls = movie.xpath("./div/div/a/@href")  # 获取电影详情链接
            if movie_urls:
                # 电影详情链接
                movie_url = TMDB_BASE_URL + movie_urls[0]
                # 发送请求，获取电影详情数据
                movie_info = get_movie_info(movie_url)
                all_movie.append(movie_info)

    print("获取到所有的电影详情，保存数据到csv.....")
    #保存数据，保存为csv文件
    save_movie(all_movie)

if __name__ == '__main__':
    main()



