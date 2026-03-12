from wordcloud import WordCloud
import io
import base64

FONT_PATH = "C:/Windows/Fonts/msgothic.ttc"

def generate_wordcloud(freq_dict):
    wc = WordCloud(
        font_path=FONT_PATH,
        width=900,
        height=450,
        background_color="white"
    ).generate_from_frequencies(freq_dict)

    img_buffer = io.BytesIO()
    wc.to_image().save(img_buffer, format="PNG")

    return base64.b64encode(img_buffer.getvalue()).decode()
