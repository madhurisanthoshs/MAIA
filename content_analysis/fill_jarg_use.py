from g4f.client import Client
import time
import ast
from content_analysis.transcription import AudioTranscriber
import asyncio
from asyncio import WindowsSelectorEventLoopPolicy
# Set the event loop policy to avoid the warning
asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
# from setup import *
from utils import report_generation

import ast

def filler_jargon(transcript):
    prompt = (
        "{ans}\nThe above is a transcript of a response from a mock interview. You are an expert on interviews. "
        "Your task is to strictly extract and return ONLY:\n"
        "1. A list of filler words (e.g., 'um', 'uh', 'hm', 'okay', 'like', 'you know', 'so', 'kind of', 'I mean', "
        "'well', 'actually', 'right', 'basically', 'sort of', 'you see', 'literally', 'alright', 'just', 'totally', "
        "'honestly', 'huh').\n"
        "2. A list of jargon words (technical or domain-specific terms that may be difficult for a general audience to understand).\n\n"
        
        "Your response MUST follow these strict formatting rules:\n"
        "- Exactly two lines only.\n"
        "- The first line must contain a Python list of filler words, each word inside double quotes. If none are found, return an empty list: [].\n"
        "- The second line must contain a Python list of jargon words, each word inside double quotes. If none are found, return an empty list: [].\n"
        "- No additional text, explanation, commentary, or empty lines.\n\n"
        
        "**Example Outputs:**\n"
        "Correct examples:\n"
        '["um", "like", "so"]\n["synergy", "KPI"]\n'
        '[]\n["blockchain", "scalability"]\n'
        '["uh", "okay"]\n[]\n'
        '[]\n[]\n\n'
        
        "**Important Notes:**\n"
        "- If a filler word appears multiple times, it should still be included in the list.\n"
        "- Do not exclude subtle filler words (e.g., 'I mean', 'you know', 'right').\n"
        "- If there are no filler or jargon words, return exactly: []\n[].\n\n"

        "Begin now:"
    )

    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt.format(ans=transcript)}],
    )
    result = response.choices[0].message.content
    lines = result.strip().split("\n")
    if len(lines) != 2:
        print(f"here: {lines}")
        filler_words, jargon_words = lines[0], []
    else:
        try:
            filler_words = ast.literal_eval(lines[0]) if lines[0].strip() else []
            jargon_words = ast.literal_eval(lines[1]) if lines[1].strip() else []
        except (SyntaxError, ValueError):
            filler_words, jargon_words = [], []    
    return filler_words, jargon_words


def calc_filler_jargon_score(transcript, filler_count, jargon_count):
    total_words = max(len(transcript.split()), 1)  # Avoid division by zero
    max_allowed_jargon = total_words * 0.1
    excess_jargon = max(0, jargon_count - max_allowed_jargon)
    filler_penalty = filler_count * 2
    jargon_penalty = excess_jargon * 0.75
    penalty = (filler_penalty + jargon_penalty) / total_words
    score = round(max(10, 100 - (penalty * 150)))
    return score


def prompt_formatting(score,transcript,filler_words,jargon_words):
    prompt = f"'{transcript}'\n the above is a transcript from a mock interview that received a score of '{score}' for jargon and filler word analysis.\njargon words identified: {jargon_words}\nfiller words identified={filler_words}\nYou are an expert on interviews. Analyze the above transcript critically, and provide helpful, actionable tips on how the user can reduce filler word and jargon usage in their responses and thus improve their score.\n answer format: \n'what you did right:' followed by a brief bulleted list of things the user did right \n'Tips for improvement:' followed by a brief bulleted list of tips, outlining concisely in each tip what the user can improve, why it's relevant from an interview standpoint, and how the user can improve it. \neach tip should be 1 sentence long. Do not reply in markdown format, just give me clean text with points"
    return prompt

def filljarg(audio_path):
    a = AudioTranscriber()
    transcript=a.transcribe(audio_path)
    filler_words,jargon_words=filler_jargon(transcript)
    score=calc_filler_jargon_score(transcript,len(filler_words),len(jargon_words))
    return score

if __name__ == "__main__":
    # transcript="H-hi, I'm Anirudh, nice to uh meet you. I hope we'll like, work well together. Given my um, experience in full-stack development, I'm kind of proficient in leveraging you know, asynchronous microservices architecture, optimizing RESTful API endpoints, and hmm, implementing scalable CI/CD pipelines for automated deployments."
    transcript2="Hi, I'm Anirudh, nice to meet you. I look forward to working together. I have experience in full-stack development and specialize in building efficient, reliable web applications. I focus on improving system performance, designing well-structured APIs, and automating deployment processes to ensure smooth operations."
    audio_path = r"..\1_audio\aud_1.wav"
    try:
        a = AudioTranscriber()
        transcript=a.transcribe(audio_path)
        filler_words,jargon_words=filler_jargon(transcript)
        print("filler words: ",filler_words,"\n jargon words: ",jargon_words)
        #print(len(transcript.split()),len(filler_words),len(jargon_words))
        score=calc_filler_jargon_score(transcript,len(filler_words),len(jargon_words))
        print(f"filler/jargon analysis score: {score:.2f}%")
        prompt = prompt_formatting(score,transcript,filler_words,jargon_words)
        report=report_generation(prompt)
        print("\n\nREPORT:\n\n", report)
    except FileNotFoundError:
        print("Take the mock interview first, please!")
