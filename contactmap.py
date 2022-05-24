import folium
import pymysql
from coordinate_transfer import wgs84_to_gcj02
from flask import Flask


#connect to db
db = pymysql.connect(host='47.113.187.45',
                     user='root',
                     password='123456',
                     database='touch')
#create a cursor
cursor = db.cursor()
#get data from db
sql = """SELECT * FROM touch"""
try:
    # 执行SQL语句
    cursor.execute(sql)
    # 获取所有记录列表
    results = cursor.fetchall()
except:
    print ("Error: unable to fetch data")
db.commit()


#add map, lines, points
study_area = folium.Map([40.70,111.397106],zoom_start = 10
   ,tiles='https://webrd02.is.autonavi.com/appmaptile?lang=zh_en&size=1&scale=1&style=8&x={x}&y={y}&z={z}',attr='高德-中英文对照')
colors = ["blue","yellow","orange","green","grey","purple","black","Cyan","magenta","#ADD8E6","#FFA500"]
for i in results:
    coor1 = wgs84_to_gcj02(i[1],i[2])
    coor2 = wgs84_to_gcj02(i[5],i[6])
    folium.Circle(coor1,color = "red").add_to(study_area)
    folium.Circle(coor2,color = "red").add_to(study_area)
    folium.PolyLine([coor1,coor2],color = colors[i[9]],weight=1).add_to(study_area)
cursor.close()
db.close()
# method for legend
def add_categorical_legend(folium_map, title, colors, labels):
    if len(colors) != len(labels):
        raise ValueError("colors and labels must have the same length.")

    color_by_label = dict(zip(labels, colors))
    
    legend_categories = ""     
    for label, color in color_by_label.items():
        legend_categories += f"<li><span style='background:{color}'></span>{label}</li>"
        
    legend_html = f"""
    <div id='maplegend' class='maplegend'>
      <div class='legend-title'>{title}</div>
      <div class='legend-scale'>
        <ul class='legend-labels'>
        {legend_categories}
        </ul>
      </div>
    </div>
    """
    script = f"""
        <script type="text/javascript">
        var oneTimeExecution = (function() {{
                    var executed = false;
                    return function() {{
                        if (!executed) {{
                             var checkExist = setInterval(function() {{
                                       if ((document.getElementsByClassName('leaflet-top leaflet-right').length) || (!executed)) {{
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].style.display = "flex"
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].style.flexDirection = "column"
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].innerHTML += `{legend_html}`;
                                          clearInterval(checkExist);
                                          executed = true;
                                       }}
                                    }}, 100);
                        }}
                    }};
                }})();
        oneTimeExecution()
        </script>
      """
   

    css = """

    <style type='text/css'>
      .maplegend {
        z-index:9999;
        float:right;
        background-color: rgba(255, 255, 255, 1);
        border-radius: 5px;
        border: 2px solid #bbb;
        padding: 10px;
        font-size:12px;
        positon: relative;
      }
      .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
        }
      .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
        }
      .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
        }
      .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 16px;
        width: 30px;
        margin-right: 5px;
        margin-left: 0;
        border: 0px solid #ccc;
        }
      .maplegend .legend-source {
        font-size: 80%;
        color: #777;
        clear: both;
        }
      .maplegend a {
        color: #777;
        }
    </style>
    """

    folium_map.get_root().header.add_child(folium.Element(script + css))

    return folium_map

# add legend
study_area = add_categorical_legend(study_area,'图例',
                             colors = ["blue","yellow","orange","green","grey","purple","black","Cyan","magenta","#ADD8E6","#FFA500"],
                            labels = ["不详", "乘车接触","登门拜访","短暂交谈","工作接触","共同就餐","购物","核酸检出","生活接触","同时空","直接接触"])
# add title
loc = '内蒙古呼和浩特市新冠疫情集中爆发区重点人员社会关系网络图'
title_html = '''
             <h3 align="center" style="font-size:16px"><b>{}</b></h3>
             '''.format(loc)  
study_area.get_root().html.add_child(folium.Element(title_html))

# save map to html

#initiate flask
app = Flask(__name__)

@app.route('/')
def showtouch():
    return study_area._repr_html_()

if __name__ == '__main__':
    app.run(debug=True, port=5000)