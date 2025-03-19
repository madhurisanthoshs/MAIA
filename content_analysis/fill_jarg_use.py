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
    try:
        prompt = "{ans}\nThe above is a transcript of a response from a mock interview. You are an expert on interviews. Your task is to strictly extract and return ONLY:\n1. A list of filler words (e.g., 'um', 'uh', 'hm', 'okay', 'like', 'you know', 'so', 'kind of', etc.)\n2. A list of jargon words.\n\nYour response MUST be:\n- Two lines only.\n- The first line: a Python list of filler words, with each word inside double quotes.\n- The second line: a Python list of jargon words, also with each word inside double quotes.\n- No additional text, explanation, or empty lines.\n\nIf no filler or jargon words are found, output empty lists in the same two-line format. Example when no words are found: []\n[]\n\nBegin now:"
        client = Client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt.format(ans=transcript)}],
        )

        result = response.choices[0].message.content
        lines = result.strip().split("\n")
        
        if len(lines) < 2:
            raise ValueError(f"Expected 2 lines but got {len(lines)}: {lines}")
        
        filler_words = ast.literal_eval(lines[0])
        jargon_words = ast.literal_eval(lines[1])
        
        return filler_words, jargon_words

    except Exception as e:
        print(f"Error in filler_jargon(): {e}")
        print(f"Raw response:\n{result if 'result' in locals() else 'No result'}")
        # Fallback: return empty lists if something breaks
        return [], []


def calc_filler_jargon_score(transcript, filler_count, jargon_count):
    total_words = max(len(transcript.split()), 1)  # Avoid division by zero
    # Set an acceptable jargon threshold (e.g., 5% of the total words)
    max_allowed_jargon = total_words * 0.1
    excess_jargon = max(0, jargon_count - max_allowed_jargon)  # Only penalize excess jargon
    # Compute weighted penalties
    filler_penalty = filler_count * 2  # Filler words are more harmful
    jargon_penalty = excess_jargon * 0.75  # Jargon is allowed in moderation
    # Calculate total penalty
    penalty = (filler_penalty + jargon_penalty) / total_words
    score = round(max(10, 100 - (penalty * 150)), 2)  # Scale appropriately
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
