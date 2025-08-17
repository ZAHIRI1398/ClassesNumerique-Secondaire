import os
import json
import random
import string
import logging
import unicodedata
from datetime import datetime, timedelta
from functools import wraps
from analyze_fill_in_blanks_ordering import is_ordering_exercise, evaluate_ordering_exercise

def get_blank_location(global_blank_index, sentences):
    """Détermine à quelle phrase et à quel indice dans cette phrase correspond un indice global de blanc"""
    blank_count = 0
    for idx, sentence in enumerate(sentences):
        blanks_in_sentence = sentence.count('___')
        if blank_count <= global_blank_index < blank_count + blanks_in_sentence:
            # Calculer l'indice local du blanc dans cette phrase
            local_blank_index = global_blank_index - blank_count
            return idx, local_blank_index
        blank_count += blanks_in_sentence
    return -1, -1
