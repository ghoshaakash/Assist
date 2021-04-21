from youtube_search import YoutubeSearch
results = YoutubeSearch('ABCD', max_results=10).to_dict()

print(results[0]["url_suffix"])
