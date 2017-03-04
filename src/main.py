# -*- coding: utf-8 -*-

import term_analysis as ta
from data_sourcing import analysis_decider, data_router
from report.ReportManager import ReportManager
from report.data_visualisation import bar_chart, timeseries_chart
from text_wrangling import document_processing
from utils.ConfigReader import ConfigReader
from utils.TwitterAuthenticate import TwitterAuthenticate

if __name__ == '__main__':

    config = ConfigReader('resources/credentials.properties')

    twitter_connection = TwitterAuthenticate(config.consumer_key, config.consumer_secret,
                                             config.access_token_key, config.access_token_secret
                                             ).request_auth().make_connection()

    source_choice = analysis_decider()
    all_tweets = data_router(source_choice, twitter_connection)

    word_counters, tweet_dates, co_occ_matrix = document_processing(all_tweets)

    top_pairs = ta.top_cooccorrent_terms(co_occ_matrix)

    most_common_terms = word_counters['terms_counter'].most_common(20)
    most_common_hashtags = word_counters['hashtag_counter'].most_common(10)
    most_common_RT = word_counters['tag_counter'].most_common(10)

    time_series = ta.tweet_timeseries(tweet_dates)

    bar_chart('top_terms', most_common_terms)
    bar_chart('top_hashtags', most_common_hashtags)
    bar_chart('top_usertags', most_common_RT)

    timeseries_chart(time_series)

    ReportManager('user').run_report(5, 'localhost', 8000)

    prob_term_matrix, prob_terms = ta.term_probabilities(
        word_counters['doc_counter'],
        word_counters['all_counter'],
        co_occ_matrix)

    pmi = ta.calculate_pmi(prob_terms, co_occ_matrix, prob_term_matrix)
    semantic_orientation = ta.semantic_orientation(prob_terms, pmi)
    top_positive_terms, top_negative_terms = ta.top_semantic_terms(semantic_orientation, 10)
