import requests
import tempfile
import os
import re
from typing import Dict
import pymupdf
from config import Config


class Paper():
    def __init__(self, arxiv_id, title, authors, abstract, categories, published_data, pdf_url, entry_id,
                 summary=None, category=None, novelty_score=None, source=None, 
                 quality_score=0.0, author_h_indices=None, author_institutions=None, category_cosine_scores=None):
        self.arxiv_id = arxiv_id
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.categories = categories
        self.published_data = published_data
        self.pdf_url = pdf_url
        self.entry_id = entry_id
        self.summary = summary
        self.category = category
        self.novelty_score = novelty_score
        self.source = source
        self.quality_score = quality_score
        self.author_h_indices = author_h_indices
        self.author_institutions = author_institutions
        self.category_cosine_scores = category_cosine_scores

    def to_dict(self):
        """Convert Paper object to dictionary for database operations"""
        return {
            'arxiv_id': self.arxiv_id,
            'title': self.title,
            'authors': self.authors,
            'abstract': self.abstract,
            'categories': self.categories,
            'published_date': self.published_data,
            'summary': self.summary or '',
            'category': self.category or '',
            'novelty_score': self.novelty_score or 0.0,
            'source': self.source or 'arxiv'
        }

    def __str__(self):
        return f"Arxiv id: {self.arxiv_id}\nTitle: {self.title}\nAuthors: {self.authors}\nAbstract: {self.abstract}\nCategories: {self.categories}\nPublished data: {self.published_data}\nPDF url: {self.pdf_url}\nEntry id: {self.entry_id}"

    def download_paper(self, paper_url: str) -> str:
        """Download a paper with retry logic and robust error handling"""
        import time
        import random

        # Retry configuration from config
        max_retries = Config.PDF_DOWNLOAD_MAX_RETRIES
        base_timeout = Config.PDF_DOWNLOAD_TIMEOUT
        retry_delays = Config.PDF_DOWNLOAD_RETRY_DELAYS

        # User agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        for attempt in range(max_retries):
            try:
                # Progressive timeout: increase timeout for each retry
                timeout = base_timeout + (attempt * 15)

                print(f"Downloading PDF (attempt {attempt + 1}/{max_retries}): {paper_url}")

                # Make request with headers and timeout
                response = requests.get(
                    paper_url,
                    timeout=timeout,
                    headers=headers,
                    stream=True  # Stream for large files
                )
                response.raise_for_status()

                # Create temporary file
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')

                # Stream content to file to handle large PDFs
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)

                tmp_file.close()

                # Verify file was downloaded successfully
                min_size_bytes = Config.PDF_MIN_SIZE_KB * 1024
                if os.path.getsize(tmp_file.name) > min_size_bytes:
                    print(f"Successfully downloaded PDF: {os.path.getsize(tmp_file.name)} bytes")
                    return tmp_file.name
                else:
                    raise Exception(
                        f"Downloaded file is too small ({os.path.getsize(tmp_file.name)} bytes), likely corrupted")

            except requests.exceptions.Timeout as e:
                print(f"Timeout on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt] + random.uniform(0, 2)  # Add jitter
                    print(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    raise Exception(f"Failed to download PDF after {max_retries} attempts: Timeout")

            except requests.exceptions.ConnectionError as e:
                print(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt] + random.uniform(0, 2)
                    print(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    raise Exception(f"Failed to download PDF after {max_retries} attempts: Connection error")

            except requests.RequestException as e:
                print(f"Request error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt] + random.uniform(0, 2)
                    print(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    raise Exception(f"Failed to download PDF after {max_retries} attempts: {str(e)}")

            except Exception as e:
                print(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt] + random.uniform(0, 2)
                    print(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    raise Exception(f"Failed to download PDF after {max_retries} attempts: {str(e)}")

        raise Exception(f"Failed to download PDF after {max_retries} attempts")

    def extract_important_sections(self, pdf_path: str) -> Dict[str, str]:
        """Extract important sections from PDF using multiple robust strategies"""
        try:
            doc = pymupdf.open(pdf_path)
            full_text = ""

            # Extract text from all pages
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                full_text += page.get_text()

            doc.close()

            # Clean and normalize text
            full_text = self._clean_text(full_text)

            # Extract key content using multiple robust strategies
            extracted_content = {}

            # 1. Extract Abstract using multiple strategies
            abstract = self._extract_abstract_robust(full_text)
            if abstract:
                extracted_content['abstract'] = abstract

            # 2. Extract Introduction using multiple strategies
            introduction = self._extract_introduction_robust(full_text)
            if introduction:
                extracted_content['introduction'] = introduction

            # 3. Extract Conclusion using multiple strategies
            conclusion = self._extract_conclusion_robust(full_text)
            if conclusion:
                extracted_content['conclusion'] = conclusion

            # 4. Extract key contributions and novelty statements
            contributions = self._extract_contributions_robust(full_text)
            if contributions:
                extracted_content['contributions'] = contributions

            # 5. Add full text for fallback
            extracted_content['full_text'] = full_text

            return extracted_content

        except Exception as e:
            print(f"Error extracting sections from PDF: {e}")
            return {'full_text': '', 'error': str(e)}

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove page numbers and headers
        text = re.sub(r'\b\d+\s*$', '', text, flags=re.MULTILINE)
        # Remove arXiv header
        text = re.sub(r'arXiv:\d+\.\d+v\d+\s*\[.*?\]\s*\d+\s*\w+\s*\d+', '', text)
        return text.strip()

    def _extract_abstract(self, text: str) -> str:
        """Extract abstract using multiple patterns"""
        patterns = [
            r'Abstract[:\-\s]*(.*?)(?=\n\s*\n|\n\s*[A-Z]|\n\s*I\.|INTRODUCTION)',
            r'ABSTRACT[:\-\s]*(.*?)(?=\n\s*\n|\n\s*[A-Z]|\n\s*I\.|INTRODUCTION)',
            r'Abstract[:\-\s]*(.*?)(?=\n\s*Index|\n\s*Keywords)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                abstract = match.group(1).strip()
                # Clean up the abstract
                abstract = re.sub(r'\n+', ' ', abstract)
                abstract = re.sub(r'\s+', ' ', abstract)
                if len(abstract) > 100:  # Ensure it's substantial
                    return abstract[:2000]  # Limit length
        return ""

    def _extract_introduction(self, text: str) -> str:
        """Extract introduction focusing on problem statement and contributions"""
        patterns = [
            r'I\.\s*INTRODUCTION[:\-\s]*(.*?)(?=\s*II\.|\s*2\.|\s*RELATED|\s*III\.)',
            r'1\.\s*INTRODUCTION[:\-\s]*(.*?)(?=\s*II\.|\s*2\.|\s*RELATED|\s*III\.)',
            r'INTRODUCTION[:\-\s]*(.*?)(?=\s*II\.|\s*2\.|\s*RELATED|\s*III\.)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                intro = match.group(1).strip()
                # Clean up the introduction text
                intro = re.sub(r'\n+', ' ', intro)
                intro = re.sub(r'\s+', ' ', intro)
                if len(intro) > 100:  # Ensure it's substantial
                    return intro[:2000]  # Limit length
        return ""

    def _extract_conclusion(self, text: str) -> str:
        """Extract conclusion focusing on results and impact"""
        patterns = [
            r'VI\.\s*CONCLUSION[:\-\s]*(.*?)(?=\s*ACKNOWLEDGMENT|\s*REFERENCES|\s*APPENDIX)',
            r'6\.\s*CONCLUSION[:\-\s]*(.*?)(?=\s*ACKNOWLEDGMENT|\s*REFERENCES|\s*APPENDIX)',
            r'CONCLUSION[:\-\s]*(.*?)(?=\s*ACKNOWLEDGMENT|\s*REFERENCES|\s*APPENDIX)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                conclusion = match.group(1).strip()
                conclusion = re.sub(r'\n+', ' ', conclusion)
                conclusion = re.sub(r'\s+', ' ', conclusion)
                return conclusion[:2000]  # Limit length
        return ""

    def _extract_contributions(self, text: str) -> str:
        """Extract key contributions and novelty statements"""
        # Look for contribution statements
        contribution_patterns = [
            r'contributions?\s*(?:are|is|include|summarized)\s*(?:as|in)\s*follows?[:\-\s]*(.*?)(?=\s*II\.|\s*III\.|\s*RELATED|\s*METHOD)',
            r'our\s+contributions?\s*(?:are|is|include)[:\-\s]*(.*?)(?=\s*II\.|\s*III\.|\s*RELATED|\s*METHOD)',
            r'we\s+(?:introduce|propose|present|develop)\s+(.*?)(?=\s*II\.|\s*III\.|\s*RELATED|\s*METHOD)',
            r'novel\s+(?:framework|method|approach|model)[:\-\s]*(.*?)(?=\s*II\.|\s*III\.|\s*RELATED|\s*METHOD)',
        ]

        contributions = []
        for pattern in contribution_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                contribution = match.group(1).strip()
                contribution = re.sub(r'\n+', ' ', contribution)
                contribution = re.sub(r'\s+', ' ', contribution)
                if len(contribution) > 50:  # Ensure it's substantial
                    contributions.append(contribution[:1000])

        if contributions:
            return ' '.join(contributions[:3])  # Take first 3 contributions
        return ""

    def _extract_abstract_robust(self, text: str) -> str:
        """Extract abstract using multiple robust strategies"""
        # Strategy 1: Try existing regex patterns
        abstract = self._extract_abstract(text)
        if abstract:
            return abstract

        # Strategy 2: Look for common abstract indicators
        abstract_indicators = [
            'abstract', 'summary', 'overview', 'introduction'
        ]

        # Find the first occurrence of any abstract indicator
        earliest_pos = len(text)
        best_match = ""

        for indicator in abstract_indicators:
            pos = text.lower().find(indicator)
            if pos != -1 and pos < earliest_pos:
                earliest_pos = pos
                # Extract text after the indicator
                start_pos = pos + len(indicator)
                # Look for the end of the abstract (next section or end of text)
                end_indicators = ['introduction', 'related work', 'background', 'method', 'approach', 'i.', '1.', 'I.']
                end_pos = len(text)

                for end_indicator in end_indicators:
                    end_pos_candidate = text.lower().find(end_indicator, start_pos)
                    if end_pos_candidate != -1 and end_pos_candidate < end_pos:
                        end_pos = end_pos_candidate

                candidate = text[start_pos:end_pos].strip()
                if len(candidate) > 200 and len(candidate) < 3000:  # Reasonable length
                    best_match = candidate

        if best_match:
            # Clean up the extracted text
            best_match = re.sub(r'\s+', ' ', best_match)
            return best_match[:2000]

        # Strategy 3: Extract first substantial paragraph
        paragraphs = text.split('. ')
        for para in paragraphs[:3]:  # Check first 3 paragraphs
            if len(para) > 100 and len(para) < 1000:
                # Check if it looks like an abstract (mentions problem, approach, etc.)
                abstract_keywords = ['propose', 'introduce', 'present', 'develop', 'method', 'approach', 'framework']
                if any(keyword in para.lower() for keyword in abstract_keywords):
                    return para[:2000]

        return ""

    def _extract_introduction_robust(self, text: str) -> str:
        """Extract introduction using multiple robust strategies"""
        # Strategy 1: Try existing regex patterns
        introduction = self._extract_introduction(text)
        if introduction:
            return introduction

        # Strategy 2: Look for introduction section markers
        intro_markers = [
            'introduction', 'background', 'motivation', 'problem statement'
        ]

        for marker in intro_markers:
            pos = text.lower().find(marker)
            if pos != -1:
                # Extract text after the marker
                start_pos = pos + len(marker)
                # Look for the end of introduction
                end_markers = ['related work', 'method', 'approach', 'proposed', 'contribution', 'ii.', '2.', 'II']
                end_pos = len(text)

                for end_marker in end_markers:
                    end_pos_candidate = text.lower().find(end_marker, start_pos)
                    if end_pos_candidate != -1 and end_pos_candidate < end_pos:
                        end_pos = end_pos_candidate

                candidate = text[start_pos:end_pos].strip()
                if len(candidate) > 300 and len(candidate) < 5000:
                    candidate = re.sub(r'\s+', ' ', candidate)
                    return candidate[:2000]

        # Strategy 3: Extract first substantial section after abstract
        # Find where abstract likely ends
        abstract_end_indicators = ['introduction', 'background', 'related work', 'method']
        start_pos = 0

        for indicator in abstract_end_indicators:
            pos = text.lower().find(indicator)
            if pos != -1:
                start_pos = pos
                break

        if start_pos > 0:
            # Extract next 2000 characters as potential introduction
            candidate = text[start_pos:start_pos + 2000].strip()
            if len(candidate) > 300:
                candidate = re.sub(r'\s+', ' ', candidate)
                return candidate[:2000]

        return ""

    def _extract_conclusion_robust(self, text: str) -> str:
        """Extract conclusion using multiple robust strategies"""
        # Strategy 1: Try existing regex patterns
        conclusion = self._extract_conclusion(text)
        if conclusion:
            return conclusion

        # Strategy 2: Look for conclusion section markers
        conclusion_markers = [
            'conclusion', 'summary', 'discussion', 'future work', 'limitations'
        ]

        for marker in conclusion_markers:
            pos = text.lower().find(marker)
            if pos != -1:
                # Extract text after the marker
                start_pos = pos + len(marker)
                # Look for the end of conclusion
                end_markers = ['acknowledgment', 'reference', 'appendix', 'bibliography']
                end_pos = len(text)

                for end_marker in end_markers:
                    end_pos_candidate = text.lower().find(end_marker, start_pos)
                    if end_pos_candidate != -1 and end_pos_candidate < end_pos:
                        end_pos = end_pos_candidate

                candidate = text[start_pos:end_pos].strip()
                if len(candidate) > 200 and len(candidate) < 3000:
                    candidate = re.sub(r'\s+', ' ', candidate)
                    return candidate[:2000]

        # Strategy 3: Extract last substantial section
        # Look for conclusion keywords in the last 30% of the text
        last_portion = text[int(len(text) * 0.7):]
        conclusion_keywords = ['conclude', 'summary', 'result', 'impact', 'future']

        for keyword in conclusion_keywords:
            pos = last_portion.lower().find(keyword)
            if pos != -1:
                candidate = last_portion[pos:].strip()
                if len(candidate) > 200:
                    candidate = re.sub(r'\s+', ' ', candidate)
                    return candidate[:2000]

        return ""

    def _extract_contributions_robust(self, text: str) -> str:
        """Extract contributions using multiple robust strategies"""
        # Strategy 1: Try existing regex patterns
        contributions = self._extract_contributions(text)
        if contributions:
            return contributions

        # Strategy 2: Look for contribution statements with flexible patterns
        contribution_patterns = [
            r'contributions?\s*(?:are|is|include|summarized)\s*(?:as|in)\s*follows?[:\-\s]*(.*?)(?=\s*[A-Z][A-Z]|\s*\d+\.|\s*related|\s*method)',
            r'our\s+contributions?\s*(?:are|is|include)[:\-\s]*(.*?)(?=\s*[A-Z][A-Z]|\s*\d+\.|\s*related|\s*method)',
            r'we\s+(?:introduce|propose|present|develop)\s+(.*?)(?=\s*[A-Z][A-Z]|\s*\d+\.|\s*related|\s*method)',
            r'novel\s+(?:framework|method|approach|model)[:\-\s]*(.*?)(?=\s*[A-Z][A-Z]|\s*\d+\.|\s*related|\s*method)',
            r'main\s+contributions?\s*(?:are|is|include)[:\-\s]*(.*?)(?=\s*[A-Z][A-Z]|\s*\d+\.|\s*related|\s*method)',
        ]

        contributions = []
        for pattern in contribution_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                contribution = match.group(1).strip()
                contribution = re.sub(r'\s+', ' ', contribution)
                if len(contribution) > 50:
                    contributions.append(contribution[:1000])

        if contributions:
            return ' '.join(contributions[:3])

        # Strategy 3: Look for bullet points or numbered lists that might be contributions
        lines = text.split('. ')
        contribution_lines = []

        for line in lines:
            line_lower = line.lower()
            # Check if line contains contribution indicators
            if any(keyword in line_lower for keyword in ['introduce', 'propose', 'develop', 'present', 'novel', 'new']):
                if len(line) > 30 and len(line) < 500:
                    contribution_lines.append(line)

        if contribution_lines:
            return '. '.join(contribution_lines[:5])[:2000]

        # Strategy 4: Extract sentences with contribution keywords from introduction
        intro_text = self._extract_introduction_robust(text)
        if intro_text:
            sentences = intro_text.split('. ')
            contribution_sentences = []

            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(keyword in sentence_lower for keyword in
                       ['contribution', 'introduce', 'propose', 'develop', 'novel']):
                    if len(sentence) > 20:
                        contribution_sentences.append(sentence)

            if contribution_sentences:
                return '. '.join(contribution_sentences[:3])[:2000]

        return ""

    def get_summary(self) -> Dict[str, str]:
        """Extract important sections from a paper for LLM summarization"""
        paper_url = f"https://arxiv.org/pdf/{self.arxiv_id}"
        pdf_path = None

        try:
            # Try to download the PDF
            pdf_path = self.download_paper(paper_url)

            # Extract important sections using PyMuPDF
            sections = self.extract_important_sections(pdf_path)

            # Clean up the temporary file immediately after extraction
            if pdf_path and os.path.exists(pdf_path):
                try:
                    os.unlink(pdf_path)
                except Exception as cleanup_error:
                    print(f"Warning: Could not clean up temporary file {pdf_path}: {cleanup_error}")

            # Add paper metadata
            sections['metadata'] = {
                'title': self.title,
                'authors': self.authors,
                'arxiv_id': self.arxiv_id,
                'categories': self.categories,
                'published_date': self.published_data
            }

            return sections

        except Exception as e:
            print(f"Error occurred while processing PDF for {self.arxiv_id}: {e}")

            # Return fallback data with abstract and metadata
            return {
                'error': str(e),
                'abstract': self.abstract,  # Use the abstract we already have
                'full_text': self.abstract,  # Use abstract as fallback
                'metadata': {
                    'title': self.title,
                    'authors': self.authors,
                    'arxiv_id': self.arxiv_id,
                    'categories': self.categories,
                    'published_date': self.published_data
                }
            }

        finally:
            # Clean up temporary file if it exists (only if not already cleaned up)
            if pdf_path and os.path.exists(pdf_path):
                try:
                    os.unlink(pdf_path)
                except Exception as cleanup_error:
                    print(f"Warning: Could not clean up temporary file {pdf_path}: {cleanup_error}")
