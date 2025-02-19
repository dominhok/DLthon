import os
from google.cloud import translate_v2 as translate
import pandas as pd

# Google Cloud Translation 클라이언트 초기화
translate_client = translate.Client()

def translate_text(text, target_language='en'):
    if isinstance(text, list):
        result = []
        for item in text:
            translation = translate_client.translate(
                item,
                target_language=target_language
            )
            result.append(translation['translatedText'])
        return result
    
    else:
        translation = translate_client.translate(
            text,
            target_language=target_language
        )
        return translation['translatedText']

def back_translate(text, target_language='en'):
    # Step 1: Translate to English
    translated_to_en = translate_text(text, target_language)
    
    # Step 2: Translate back to Korean
    translated_back_to_ko = translate_text(translated_to_en, target_language='ko')
    
    return translated_back_to_ko

def process_csv(input_file, output_file, text_column='text'):
    # 입력 CSV 파일 읽기
    df_input = pd.read_csv(input_file)
    
    # 텍스트 데이터 추출
    texts = df_input[text_column].tolist()
    classes = df_input['class'].tolist()
    
    # 증식된 데이터 생성
    augmented_texts = back_translate(texts)
    
    # 새로운 인덱스 생성
    last_index = df_input['idx'].max() if not df_input.empty else -1
    new_indices = range(last_index + 1, last_index + len(augmented_texts) + 1)
    
    # 새로운 DataFrame 생성하여 원본과 증식된 데이터를 추가
    new_rows = []
    for idx, augmented, cls in zip(new_indices, augmented_texts, classes):
        new_rows.append({
            'idx': idx,
            'class': cls,
            text_column: augmented
        })
    
    df_augmented = pd.DataFrame(new_rows)
    
    # 원본 DataFrame에 증식된 데이터 추가
    df_combined = pd.concat([df_input, df_augmented], ignore_index=True)
    
    # 업데이트된 DataFrame을 원본 CSV 파일로 저장
    # output_file = input_file  # 원본 파일 덮어쓰기
    df_combined.to_csv(output_file, index=False)

# 예시 사용법
input_csv = '/Users/K010k/aiffel/train.csv'  # 입력 CSV 파일 경로
output_csv = '/Users/K010k/aiffel/train_aug.csv'  # 출력 CSV 파일 경로
text_column = 'text'  # 텍스트 데이터가 있는 열 이름

process_csv(input_csv, output_csv, text_column)