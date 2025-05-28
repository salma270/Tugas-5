from flask import Flask, render_template
from pymongo import MongoClient
import plotly.graph_objs as go
from collections import Counter
import re

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client.flo_health
collection = db.articles

@app.route("/")
def index():
    articles = list(collection.find())

    # 1. Jumlah artikel tentang menstruasi
    menstruation_keywords = ["menstruation", "period", "menstrual", "dysmenorrhea", "cramps", "cycle"]
    menstruation_count = 0
    for article in articles:
        text = (article['title'] + " " + article['content']).lower()
        if any(keyword in text for keyword in menstruation_keywords):
            menstruation_count += 1

    menstruation_pie = go.Figure(data=[go.Pie(
        labels=['Menstruation Related', 'Others'],
        values=[menstruation_count, len(articles) - menstruation_count],
        hole=0.4
    )])
    menstruation_pie.update_layout(title="Proporsi Artikel yang Membahas Menstruasi")

    # 2. Kata kunci sering di judul
    title_words = []
    for article in articles:
        title_words += re.findall(r'\b\w+\b', article['title'].lower())

    stopwords = set(['the', 'and', 'of', 'to', 'in', 'a', 'is', 'for', 'on', 'with', 'your', 'you', 'how', 'what', 'why', 'are'])
    filtered_words = [w for w in title_words if w not in stopwords and len(w) > 2]
    word_counts = Counter(filtered_words)
    most_common = word_counts.most_common(10)

    common_bar = go.Figure([go.Bar(x=[w[0] for w in most_common], y=[w[1] for w in most_common])])
    common_bar.update_layout(title="Top 10 Kata Kunci Paling Sering Muncul di Judul", xaxis_title="Kata", yaxis_title="Frekuensi")

    # 3. Kata kunci paling jarang di judul
    least_common = [word for word, count in word_counts.items() if count == 1]
    least_common_limited = least_common[:10]  # Ambil 10 teratas dari yang langka

    rare_bar = go.Figure([go.Bar(x=least_common_limited, y=[1]*len(least_common_limited))])
    rare_bar.update_layout(title="Top 10 Kata Kunci Paling Jarang Muncul di Judul", xaxis_title="Kata", yaxis_title="Frekuensi")

    # Kirim semua grafik ke template
    graphs = [
        menstruation_pie.to_html(full_html=False),
        common_bar.to_html(full_html=False),
        rare_bar.to_html(full_html=False)
    ]

    return render_template("index.html", graphs=graphs)

if __name__ == "__main__":
    app.run(debug=True)
