from flask import current_app as app
from flask import render_template, request, redirect, abort, Markup
from WhatsApp.functions import ExtractDataFrame, GenerateStats
from app.graphs import *
import os


@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404'), 404


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(os.path.join('uploads/' + uploaded_file.filename))

    return redirect(f'/process/{uploaded_file.filename}')


@app.route('/process/<file_name>')
def processing_phase(file_name):
    if file_name=='':
        abort(404)
    try:
        chats = ExtractDataFrame(os.path.join('uploads/' + file_name))
        chats.process()
        df = chats.dataframe()
        #os.remove(os.path.join('uploads/' + file_name))
        stats = GenerateStats()
        media_ratio = round(stats.mediaRatio(df),2)
        total_emojis = stats.totalEmojis(df) 
        unique_emojis = stats.uniqueEmojis(df) 
        frequent_emojis = stats.frequentEmojis(df)
        emoji_donut = frequentEmojis_donut(frequent_emojis)
        active_members = stats.activeMembers(df)
        activeMemberPlot = membersBarPlot(active_members, 'Active Members of The Group')
        lazy_members = stats.lazyMembers(df)
        lazyMemberPlot = membersBarPlot(lazy_members, 'Lazy Members of The Group')
        result_dates = stats.activityOverDates(df)
        datesActivityGraph = activityDate_Graph(result_dates)
        result_time = stats.activityOverTime(df)
        timeActivityGraph = activityTime_Graph(result_time)
        morn_night = stats.nightOwls_earlyBirds(df)
        morning = morn_night['morning']
        morning_plot = night_morningPlot(morning, 'Early Birds (6 am to 9 am)')
        night = morn_night['night']
        night_plot = night_morningPlot(night, 'Night Owls (11 pm to 3 am)')
        con_less = stats.emojiCon_Emojiless(df)
        emoji_con = con_less['Emoji_con']
        emoji_less = con_less['Emoji_less']
        holidays = stats.holidays_dict
        returned = stats.holidaysDataFrame(df)
        holiday_authors = {}
        holiday_freq_emojis = {}
        for i in holidays.values():
            if not returned[i].empty:
                holiday_authors[i] = stats.activeMembers(returned[i]).to_html()
                holiday_freq_emojis[i] = stats.frequentEmojis(returned[i]).to_html()
        
    except:
        abort(404)
    

    return render_template('analysis.html', total_emojis=total_emojis, total=df.shape[0],
                            media_ratio=media_ratio, unique_emojis=unique_emojis,
                            activeMemberPlot=activeMemberPlot, lazyMemberPlot=lazyMemberPlot,
                            bar_plot1=datesActivityGraph, bar_plot2=timeActivityGraph,
                            morning_plot=morning_plot, night_plot=night_plot,
                            emoji_con=emoji_con.to_html(classes='emoji_con'),
                            emoji_less=emoji_less.to_html(classes='emoji_less'),
                            holiday_authors=holiday_authors, holiday_freq_emojis=holiday_freq_emojis,
                            emoji_donut=emoji_donut)


# http://127.0.0.1:5000/process/WhatsApp%20Chat%20with%20Shahbad%20Roots%20-%20Family.txt