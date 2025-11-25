import re

def split_text(text: str, max_words: int = 3000, overlap_sentences: int = 1):
    text = re.sub(r"\s+", " ", text.strip())
    sentences = re.split(r'(?<=[.!?;:])\s+', text)
    chunks, current = [], []
    count = 0

    for i, s in enumerate(sentences):
        words = len(s.split())

        if words > max_words:
            parts = [" ".join(s.split()[j:j + max_words]) for j in range(0, words, max_words)]
            chunks.extend(parts)
            continue

        if count + words > max_words:
            chunks.append(" ".join(current).strip())
            overlap = sentences[max(0, i - overlap_sentences):i]
            current = overlap + [s]
            count = sum(len(x.split()) for x in current)
        else:
            current.append(s)
            count += words

    if current:
        chunks.append(" ".join(current).strip())
    return chunks


def aggregate_chunk_results(chunk_results):
    
    if not chunk_results:
        return {}

    aggregated = {}
    keys = chunk_results[0].keys()

    for key in keys:
        for result in chunk_results:
            value = result.get(key, "Not specified")
            if value and value != "Not specified":
                aggregated[key] = value
                break
        else:
            aggregated[key] = "Not specified"

    return aggregated
