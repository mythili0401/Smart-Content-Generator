import numpy as np
import pandas as pd
import webbrowser
import re
from googlesearch import search
from bing_image_urls import bing_image_urls
from bs4 import BeautifulSoup
import requests
import tkinter as tk  
import time
from azureml.core.model import Model
import json
import openai
openai.api_type = "azure"
openai.api_base = "https://newgenai-poc.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = "api key"
from nltk.tokenize import word_tokenize

def get_completion(prompt):
    response = openai.ChatCompletion.create(engine="AcademyGenAI",
               messages = [{"role": "user", "content": prompt}], temperature=0.0)
    response = response.choices[0].message["content"]
    return response

def newsletter_creation_updated(content,words):    
    words = words
    # content = [' '.join(s.split()[:2000]) for s in content]
    for i in content:
        print("Content>> ",i,"\n\n")
    
    output_format="""[
    {"title": <title of the newsletter, "introduction":<Introduction to newsletter>},
    {"topic1": <topic 1>, "content1": <content of topic 1>},
    {"topic2": <topic 2>, "content2": <content of topic 2>},
    {"topic3": <topic 3>, "content3": <content of topic 3>},
    {"topic4": <topic 4>, "content4": <content of topic 4>},
    {"topic5": <topic 5>, "content5": <content of topic 5>},
    {"topic6": <topic 6>, "content6": <content of topic 6>}]"""


    Prompt =f"""You are a newsletter creating assistant. The input content is coming from multiple sources. Use all the content provided to you, add much as information possible in the response.\
    Your task is to use all the content to create a newsletter for a well-known corporate organization.\n
    Using the content delimited in triple backticks, generate an interesting and engaging newsletter.\n
    In the reponse do not mention the word 'Newsletter'.\n
    
    ***Rephrase the content if necessary, the content should be generic in nature, it should not represent any organisation in particular.\n
    The content is for knowledge purposes only.\n***
    
    Follow the given directions while creating the newsletter:\n
    1. The newsletter should have interesting and catchy topics for every section.
    2. Provide a catchy "title" to the newsletter which should not match any of the 'topics' directly. Also provide an interesting and crisp 'introduction'. \n
    3. Each content should be detailed and elaborate. Make content as informative as possible.\n
    3. The newsletter should be in the form of topic and content pairs, that would make different sections of the final newsletter.\n
    4. Directions for output:\n
    5. Response should have only {words} words. You must strictly follow this word limit in the response. Do not mention "No of words in the response" in the output 
    6. The response should be displayed as a list of dictionary in the following format with only topics. Don't add any empty 'topics' and 'content' to the response:\n {output_format}. 
    7. Make sure all dictionaries in the response are in valid json format.
    
    Content:\n
    
    ///{content}///"""
    
    print("Entered newsletter creation function\n")
    
    try:
        newsletter_content=get_completion(Prompt)
    except:
        print("running again, token limit exceeded")
        content = [' '.join(s.split()[:2000]) for s in content]
        newsletter_content=get_completion(Prompt)
        
    
    if ',\n]' in newsletter_content:
        newsletter_content = newsletter_content.rsplit(',', 1)[0] + newsletter_content.rsplit(',', 1)[1].replace(',', '')
    
    print('newsletter_content-', newsletter_content)
    return newsletter_content

def is_blog(url):
        return 'blog' in url or 'quora' in url
    
def remove_blog_urls(url_list):
    filtered_list = [[item for item in sublist if not is_blog(item['url'])] for sublist in url_list]
    filtered_list = [sublist for sublist in filtered_list if sublist]

    return filtered_list

def extract_text_from_webpages(url_list):
    content_list = []
    for url in url_list:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            for tag in soup(["header", "footer"]):
                tag.decompose()
            main_content = soup.get_text()
            # content = main_content.replace("  "," ")
            content = re.sub(' +', ' ',main_content)
            content = content.strip()
            content = content.replace("\n","  ")
            content = content.replace("\t"," ")
            content = content[:4000]
            print("Content: ",content)
        except Exception as e:
            print("Exception : ",e)
            content = ""
        content_list.append(content)
    return content_list

def get_openai_recommendations(keywords, sources):
    
    output_format="""[
    {"keyword1": ["recommendation1, "{recommendation2",...]},
    {"keyword2": ["recommendation1, "recommendation2",...]}, 
    ...
    {"source1": ["recommendation1, "{recommendation2",...]},
    {"source2": ["recommendation1, "recommendation2",...]},...]"""
    
    prompt = f"""You are a suggestion providing assistance. Your task is to provide innovative and intersting suggestions to the keywords given to you.
    You will receive two inputs - list of keywords, list of sources. 
    The recommendation should be compact and short phrases.\n
    For every keyword from the list of keywords, provide suggestions like "latest development", "technologies trend", "new products launches" and etc. Don't use the examples listed, use your own creativity to generate new suggestions.\n
    For every source, from list of sources provide a "competing companies", "news articles", "relating publishing" and etc. Don't use the examples listed, use your own creativity to generate new suggestions.\n
    List of keywords: {keywords}\n
    List of sources: {sources}\n
    If list of sources is empty, generate own sources from the context provided and key should named as 'source'. For this case generate only 1 list of recommendation for sources.\n
    keyword or source name should not be present in any of the suggestions.
    The response should be provided in the given output format {output_format}."""
    
    recommendations_str = get_completion(prompt)
    print('--------recommendations_str: ',recommendations_str)
    recommendations_dict = eval(recommendations_str)
    print('recommendations_dict: ',recommendations_dict)

    keywords_result = {key: value for d in recommendations_dict for key, value in d.items() if key in keywords}
    print('------------keywords_result: ',keywords_result)
    
    def replace_source_with_empty_string(list_of_dicts):
        empty_keys = []
 
        for dictionary in list_of_dicts:
            for key in list(dictionary.keys()):
                if re.match(r'^source\d*$', key):
                    empty_keys.append(key)
                    dictionary[''] = dictionary.pop(key)
        return dictionary
                
    source_result = replace_source_with_empty_string(recommendations_dict)
    print('source_result: ', source_result)
    return keywords_result, source_result

def get_urls_and_descriptions(keywords, source):
    query = f"{source} {keywords} site: .com"
    url_descriptions = []
    print("Search query: ",query)
    try:
        search_result = search(query, num=10, stop=2, pause=2)
        print("search_result: ",search_result)
    except Exception as e:
            print(f"Error occurred: {e}")
    
    for url in search_result:
        try:
            print("url::", url)
            response = requests.get(url)
            # print("response::", response)
            time.sleep(1)
            soup = BeautifulSoup(response.text, 'html.parser')
            # print("soup", soup)
            title = soup.title.string
            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description['content'] if meta_description else None
            if description is None or title == "403 Forbidden":
                print("Description is None or 403, taking next url.")
            else:
                print("Description is not none, taking this url.")
                url_descriptions.append({'url': url, 'title': title, 'description': description})
                break
        except Exception as e:
            print(f"Error occurred: {e}")
    print("Extracted urls-",url_descriptions)
    return url_descriptions

## Function to search for company website
def find_company_website(keyword, company_name):
    query = f"{company_name} {keyword} site: .com"
    for url in search(query, tld="com", num=10, stop=10, pause=2):
        return url

#Function to generate serach URL for keywords and company name
def generate_search_urls(keywords, company_names):
    search_urls = []
    for keyword in keywords:
        keyword = keyword.strip()
        for company_name in company_names:
            company_name = company_name.strip()
            # url = find_company_website(keyword,company_name)
            url_descriptions = get_urls_and_descriptions(keyword, company_name)
            search_urls.append(url_descriptions)
            # search_urls.append(url)
            
    return search_urls

def is_subtopic(element):
    return element.name in ["h2", "h3", "h4", "h5"]

def find_content_for_subtopic(subtopic):
    content = []

    # Find the next element(s) following the subtopic
    next_element = subtopic.find_next()

    while next_element and not is_subtopic(next_element):
        if next_element.name == "p":
            content.append(next_element.get_text().strip())

        next_element = next_element.find_next()

    content_text = "\n".join(content)
    return content_text

def extract_keywords(keywords, sources):    
    keywords = keywords.split(',')
    keywords = keywords[:3]
    print("Length of keywords", len(keywords))
    sources = sources.split(',')
    sources = sources[:3]
    print("sources", sources)
        
    search_urls = generate_search_urls(keywords,sources)
    search_urls = [[x for x in sub if x] for sub in search_urls]
    for i in search_urls:
        print("Matched article --",i,"\n")
    return search_urls 

def extract_subtopics_from_website(website_urls):
    website_urls = website_urls.split(',')
    subtopics_dict = {} 
    for url in website_urls:
        print('Url: ',url)
        response = requests.get(url)
        #check the response status
        if response.status_code== 403:
            print(f"skipping {url} due to 403 forbidden response")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        subtopic_elements = soup.find_all(["h2", "h3", "h4", "h5"])
        for subtopic in subtopic_elements:
            subtopic_text = subtopic.get_text().strip()
            if "thank you" not in subtopic_text.lower() and "sorry" not in subtopic_text.lower():
                content = find_content_for_subtopic(subtopic) 
                subtopics_dict[subtopic_text] = content
                subtopics_dict={topic: content for topic, content in subtopics_dict.items() if topic}
                subtopics_dict={topic: content for topic, content in subtopics_dict.items() if content != "" }
                    
        if response.status_code != 200:
            print(f"skipping url {url} due to error. Status code: {response.status_code}")

    topics = subtopics_dict.keys()
    final_topics = extract_clean_topics(topics)
    final_topics = final_topics[1:-1]  
    final_topics = final_topics.split(",") 
    final_topics = [x.replace('"','') for x in final_topics]
    final_topics = [x.replace("'",'') for x in final_topics]

    return final_topics, subtopics_dict

def extract_subtopics_from_website_1(website_urls):
    website_urls = website_urls.split(',')
    subtopics_dict = {} 
    for url in website_urls:
        print('Url: ',url)
        response = requests.get(url)
        #check the response status
        if response.status_code== 403:
            print(f"skipping {url} due to 403 forbidden response")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        subtopic_elements = soup.find_all(["h2", "h3", "h4", "h5"])
        subtopic_count = 0
        for subtopic in subtopic_elements:
            subtopic_text = subtopic.get_text().strip()
            if "thank you" not in subtopic_text.lower() and "sorry" not in subtopic_text.lower():
                content = find_content_for_subtopic(subtopic) 
                subtopics_dict[subtopic_text] = content
                subtopics_dict={topic: content for topic, content in subtopics_dict.items() if topic}
                subtopics_dict={topic: content for topic, content in subtopics_dict.items() if content != "" }
                
                subtopic_count += 1
                if subtopic_count == 3:
                    break
                    
        if response.status_code != 200:
            print(f"skipping url {url} due to error. Status code: {response.status_code}")

    topics = subtopics_dict.keys()
    final_topics = extract_clean_topics(topics)
    final_topics = final_topics[1:-1]  
    final_topics = final_topics.split(",") 
    final_topics = [x.replace('"','') for x in final_topics]
    final_topics = [x.replace("'",'') for x in final_topics]

    return final_topics, subtopics_dict

def generation(selected_topics,topics_and_content):
    print("selected_topics by users", selected_topics)
    content_list=[]
    print('Topic type::', type(selected_topics))
    print('Topic and content type::', type(topics_and_content))
    
    print("topics from topics_and_content",topics_and_content.keys())
    
    
    for i in topics_and_content.keys():
            for j in selected_topics.split(','):
                if j.strip()==i.strip():
                    content=topics_and_content[i]  
                    print("\nMatching content--",i)
                    content_list.append(content)
                    
    print('\ncontent from topic:\n',len(content_list))
    print('\n',content_list)
    print("selected_topics after loop::", selected_topics)
    print("content_list after loop::", content_list)
    
    return selected_topics, content_list

def extract_subtopics_content_from_text(text):

    output_format="""{
    <topic 1>:<content of topic 1>, 
    <topic 2>:<content of topic 2>,
    <topic 3>:<content of topic 3>,
    <topic 4>:<content of topic 4>,
    <topic 5>:<content of topic 5>,
    <topic 6>:<content of topic 6>}"""
    
    
#     output_format="""{
#     "Topic":<topic 1>, "Content":<content of topic 1>, 
#     "Topic":<topic 2>, "Content":<content of topic 2>,
#     "Topic":<topic 3>, "Content":<content of topic 3>,
#     "Topic":<topic 4>, "Content":<content of topic 4>,
#     "Topic":<topic 5>, "Content":<content of topic 5>,
#     "Topic":<topic 6>, "Content":<content of topic 6>}
#     """

 
    prompt=f"""
    You are a newsletter generating assitant. Your task is to extract relevant topics and its content from the provided text delimited in triple asterisks.
    Each topic and content pair will be used to create a section of the newsletter.\n
    ***{text}***
    The output should be a dictionary with topics as keys and corresponding content as values in the following format:\n {output_format}."""
    
    topics_content_dict=get_completion(prompt)
    
    topics_content_dict = eval(topics_content_dict)
    
    print("Type--",type(topics_content_dict))

    return topics_content_dict

def newsletter_creation(topics,content,words):
    # with open('newsletter_tone.txt','r') as file:
    #     sample_tone=file.read()
    #     sample_tone=sample_tone.replace('\n',' ')
    
    topics_list = list(topics.split(","))
    print('topics_list: ',len(topics_list))
    topic_len = len(topics_list)
    
    output_format="""[
    {"title": <title of the newsletter, "introduction":<Introduction to newsletter>},
    {"topic1": <topic 1>, "content1": <content of topic 1>},
    {"topic2": <topic 2>, "content2": <content of topic 2>},
    {"topic3": <topic 3>, "content3": <content of topic 3>},
    {"topic4": <topic 4>, "content4": <content of topic 4>},
    {"topic5": <topic 5>, "content5": <content of topic 5>},
    {"topic6": <topic 6>, "content6": <content of topic 6>}]"""

    Prompt =f"""You are a newsletter creating assistant. The input content is coming from multiple sources.\
    Your task is to use all the content to create a newsletter for a well-known corporate organization.\n
    Using the content delimited in triple backticks, generate an interesting and engaging newsletter.\n
    
    ***The content should be generic in nature, it should not represent any organisation in particular.\n
    The content is for knowledge purposes only.\n***
    
    Follow the given directions while creating the newsletter:\n
    1. The newsletter should have only the topics provided to you. eg: if 2 topics are provided, newsletter should be created with only same 2 topics.\n
    2. Provide a catchy "title" to the newsletter which should not match any of the 'topics' directly. Also provide an interesting and crisp 'introduction'. \n
    3. Each content 
    3. The newsletter should be in the form of topic and content pairs, that would make different sections of the final newsletter.\n
    4. Directions for output:\n
    5. Number of words in the response: {words}. You must follow this word limit in the response. Do not mention "No of words in the response" in the output 
    6. The response should be displayed as a list of dictionary in the following format with only {topic_len} topics. Don't add any empty 'topics' and 'content' to the response:\n {output_format} based on {topic_len}. 
    7. Make sure all dictionaries in the response are in valid json format.
    8. Use only the following topics while generating the response. Do not add or create any new topics.\n 
    topics: {topics} \n
    
 
    
    
    Content:\n
    
    ///{content}///"""

    newsletter_content=get_completion(Prompt)
    if ',\n]' in newsletter_content:
        newsletter_content = newsletter_content.rsplit(',', 1)[0] + newsletter_content.rsplit(',', 1)[1].replace(',', '')
    
    # print('newsletter_content', newsletter_content)
    return newsletter_content

def extract_generated_topics(newsletter_topic):
    new =[]
        
    # prompt = f"Extract the topics from the given newsletter content{newsletter_topic} and save it in a {new} list"
    prompt = f""" your task is to extract only the topics mentioned in the given text. The topics will be written
    after the tag <topic1>, <topic2> and so on. Do not introduce any new topics only extract the ones explicilty mention in the text./n
    The 'title' should not be listed as a topic.
    The response should be a list of extracted topics./n
    text: {newsletter_topic}
    """
    
    
    newsletter_topic = get_completion(prompt)
    
    newsletter_topic = eval(newsletter_topic)
    print("List of extracted topics and type of response", newsletter_topic, type(newsletter_topic))
    return newsletter_topic

def get_image_urls_for_topics(topics, limit=2):
    image_urls_dict = {}
 
    for term in topics:
        urls = bing_image_urls(term, limit=limit)
        if urls:
            valid_urls = [url for url in urls if "https://miro.medium.com/max/4266/1*EESGJiqpopRk3A2QHd5NUw.png" not in url]
            if valid_urls:
                image_urls_dict[term] = [valid_urls[0]]
 
    return image_urls_dict


def unique_urls(url_list):
    unique_list = []
    seen_urls = set()

    for entry in url_list:
        url = entry[0]['url']
        if url not in seen_urls:
            seen_urls.add(url)
            unique_list.append(entry)

    return unique_list

def short_description(keyword):
    output_format = """{<"title">:<"Brief on {keyword}>",
    <"content">:<"description">}"""

    prompt=f"""You are a short description provider Assistant, your task is to generate informative descriptions about the provided keyword {keyword} in just 3 lines.\n
    Ensure the descriptions are up-to-date with the latest information and contain relevant updates and trends\n
    The response should be provided in the given output format {output_format}.
    """
    short_description=get_completion(prompt)
    short_description = eval(short_description)
    return short_description

def get_openai_recommendations_1(keywords):
    
    output_format="""[
    {"keyword1": ["recommendation1, "{recommendation2",...]},
    {"keyword2": ["recommendation1, "recommendation2",...]}, 
    ...]"""
    
    prompt = f"""You are a suggestion providing assistance. Your task is to provide innovative and intersting suggestions to the keywords given to you.
    You will receive one input - list of keywords. 
    The recommendation should be compact and short phrases.\n
    For every keyword from the list of keywords, provide suggestions like "latest development", "technologies trend", "new products launches" and etc. Don't use the examples listed, use your own creativity to generate new suggestions.\n
    List of keywords: {keywords}\n
    keyword name should not be present in any of the suggestions.
    The response should be provided in the given output format {output_format}."""
    
    recommendations_str = get_completion(prompt)
    # print('--------recommendations_str: ',recommendations_str)
    recommendations_dict = eval(recommendations_str)
    # print('recommendations_dict: ',recommendations_dict)

    keywords_result = {key: value for d in recommendations_dict for key, value in d.items() if key in keywords}
    # print('------------keywords_result: ',keywords_result)
                
    return keywords_result

def top_companies(keywords):
    output_format="""[
    {"keyword1": ["recommendation1, "{recommendation2",...]},
    {"keyword2": ["recommendation1, "recommendation2",...]}, 
    ...]"""
        
    prompt = f""" You are a suggestion providing assistance. 
    Your task is to provide a list of top consulting companies and their top competitors based on the given keywords {keywords}.\n
    You will receive one input - list of keywords.\n
    List of keywords: {keywords}\n
    keyword name should not be present in any of the suggestions.
    The response should be provided in the given output format {output_format}."""
    
    response = get_completion(prompt)
    
    output_cleaned = response.replace('\n', '')
    top_comp = json.loads(output_cleaned)
    top_companies_1 = [value for dictionary in top_comp for value_list in dictionary.values() for value in value_list]
    top_companies = list(set(top_companies_1))

    return top_companies

def get_search_url(keyword, company_name):
    query = f"{keyword} {company_name}"
    try:
        search_results = search(query, num=1, stop=1, pause=2)
        search_url = next(search_results)
        return {"display": company_name, "link": search_url}
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def generate_search_urls_new(keywords, company_names):
    links_result = {}
    
    if isinstance(keywords, str):
        keywords = [keywords]
    if isinstance(keywords, str):
        company_names = [company_names]
        
    for keyword in keywords:
        keyword = keyword.strip()
        links_result[keyword] = []
        for company_name in company_names:
            company_name = company_name.strip()
            url_link = get_search_url(keyword, company_name)
            if url_link:
                links_result[keyword].append(url_link)
    return links_result

def split_content_and_create_bullet(output):
    modified_output = []
    bullet_index = 1
    for item in eval(output):
        modified_item = {}
        modified_item.update(item)
        content_key = f'content{bullet_index}'
        if content_key in item:
            sentences = item[content_key].split('. ')
            bullet_key = f'bullet{bullet_index}'
            modified_item[bullet_key] = sentences
            bullet_index += 1
        modified_output.append(modified_item)
    return modified_output
 
def bullets(newsletter):
    newsletter_bullet_1 = split_content_and_create_bullet(newsletter)
    newsletter_bullet = []
    for dictionary in newsletter_bullet_1:
        new_dict = {}
        for key, value in dictionary.items():
            new_key = str(key).replace("'","\"")
            new_value = str(value).replace("'","\"")
            new_dict[new_key] = new_value
        newsletter_bullet.append(new_dict)
    return newsletter_bullet

from urllib.parse import urlparse
 
def extract_company_name(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc:
        parts = parsed_url.netloc.split('.')
        if len(parts) >= 2:
            return parts[-2]
    return None

def camel_case(s):
    words = s.split('_')
    return ''.join(word.title() for word in words)

def init():
    
    print("init done")
    
def main(data):
    
    input_data = data["data"]
    words = input_data["words"]
    key = input_data["key"]
    # output_format = input_data["output_format"]

    # output_format = "paragraph" or output_format = "bullet"

    if key == "keywords_1":
        keywords = input_data["keywords"]
        short_description_1 = short_description(keywords)
        keywords_result = get_openai_recommendations_1(keywords)
        top_companies_1 = top_companies(keywords)
        # print("top_companies------:",top_companies_1)
        urls = generate_search_urls_new(keywords, top_companies_1)
        result = {"key": key, "description":short_description_1, "keywords_result":keywords_result, "links_result":urls}

        # resp = AMLResponse(result,200,json_str=True)

        return result

    elif key == "keywords_2":
        print('key----------',key)
        print('inside keywords2-------------------')
        website_urls = input_data["urls"]
        website_urls = website_urls.split(',')
        # print("website_urls---------",website_urls)

        keywords = input_data["keywords"]
        recommendation = input_data["recommendations"]
        recommendation = recommendation.split(',')
        urls_output = generate_search_urls_new(keywords, recommendation)

        for key, value in urls_output.items():
            for item in value:
                company_name = extract_company_name(item['link'])
                if company_name:
                    item['display'] = camel_case(company_name)
        
        print('************urls_output--------------:',urls_output)                    
        links = [item['link'] for sublist in urls_output.values() for item in sublist if not is_blog(item['link'])]
        # print("links-----:",links)

        website_urls.extend(links)
        combined_urls = website_urls
        unique_links = set(combined_urls)

        print("unique_links-------",unique_links)

        extracted_content = extract_text_from_webpages(unique_links)
        # print("extracted_content---------",type(extracted_content))

        input_text = input_data["inputText"]
        input_text = [input_text]

        extracted_content.extend(input_text)
        combined_extracted_content = extracted_content
        print("combined_extracted_content:   ",combined_extracted_content)

        # words = input_data["words"]
        # print("words", words)   
        output_layout = input_data['output_layout']
        if output_layout =='A4 - 1 page layout':
            words = '200'
        elif output_layout =='A4 - 2 page layout':
            words = '400'
        elif output_layout =='A4 - 3 page layout':
            words = '600'
        else:
            words = '1000'
            

        output_format = input_data['output_format']
        print('output_format---------',output_format)
        
        newsletter1 = newsletter_creation_updated(combined_extracted_content,words)
        
        if output_format == 'Mostly bullets':
            newsletter_output = bullets(newsletter1)
        else:
            print('================inside else=========================')
            newsletter_output = newsletter1

        generated_topics = extract_generated_topics(newsletter1)


        image_urls = get_image_urls_for_topics(generated_topics)
        print("-----------image_urls----------",image_urls)
        output_references_1 = input_data['output_references']
        print('output_references_1---------------',output_references_1)
        
        if output_references_1 == 'Hyperlinks':
            output_references_2 = list(unique_links)
            # output_references_2 = ','.join(output_references_2)
            output_references_2 = ','.join([item for item in output_references_2 if item.strip()])

        else:
            output_references_2 = urls_output

        print('---output_references------------------',output_references_2)
        print('key-------------',key)
        # print("image_urls -",image_urls)

        result = {"key": key,"content": newsletter_output, "image_urls": image_urls,"output_references": output_references_2}

        # resp = AMLResponse(result,200,json_str=True)
        return result

    else:
        return print("bad request")
