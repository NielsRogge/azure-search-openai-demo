from typing import Generator, List

from .pdfparser import Page

from langchain.text_splitter import RecursiveCharacterTextSplitter


class SplitPage:
    """
    A section of a page that has been split into a smaller chunk.
    """

    def __init__(self, page_num: int, text: str):
        self.page_num = page_num
        self.text = text


class TextSplitter:
    """
    Class that splits pages into smaller chunks. This is required because embedding models may not be able to analyze an entire page at once
    """

    def __init__(self, verbose: bool = False):
        self.sentence_endings = [".", "!", "?"]
        self.word_breaks = [",", ";", ":", " ", "(", ")", "[", "]", "{", "}", "\t", "\n"]
        self.max_section_length = 1000
        self.sentence_search_limit = 100
        self.section_overlap = 100
        self.verbose = verbose

    def split_pages(self, pages: List[Page]) -> Generator[SplitPage, None, None]:
        def find_page(offset):
            num_pages = len(pages)
            for i in range(num_pages - 1):
                if offset >= pages[i].offset and offset < pages[i + 1].offset:
                    return pages[i].page_num
            return pages[num_pages - 1].page_num

        all_text = "".join(page.text for page in pages)
        length = len(all_text)
        start = 0
        end = length
        while start + self.section_overlap < length:
            last_word = -1
            end = start + self.max_section_length

            if end > length:
                end = length
            else:
                # Try to find the end of the sentence
                while (
                    end < length
                    and (end - start - self.max_section_length) < self.sentence_search_limit
                    and all_text[end] not in self.sentence_endings
                ):
                    if all_text[end] in self.word_breaks:
                        last_word = end
                    end += 1
                if end < length and all_text[end] not in self.sentence_endings and last_word > 0:
                    end = last_word  # Fall back to at least keeping a whole word
            if end < length:
                end += 1

            # Try to find the start of the sentence or at least a whole word boundary
            last_word = -1
            while (
                start > 0
                and start > end - self.max_section_length - 2 * self.sentence_search_limit
                and all_text[start] not in self.sentence_endings
            ):
                if all_text[start] in self.word_breaks:
                    last_word = start
                start -= 1
            if all_text[start] not in self.sentence_endings and last_word > 0:
                start = last_word
            if start > 0:
                start += 1

            section_text = all_text[start:end]
            yield SplitPage(page_num=find_page(start), text=section_text)

            last_table_start = section_text.rfind("<table")
            if last_table_start > 2 * self.sentence_search_limit and last_table_start > section_text.rfind("</table"):
                # If the section ends with an unclosed table, we need to start the next section with the table.
                # If table starts inside sentence_search_limit, we ignore it, as that will cause an infinite loop for tables longer than MAX_SECTION_LENGTH
                # If last table starts inside section_overlap, keep overlapping
                if self.verbose:
                    print(
                        f"Section ends with unclosed table, starting next section with the table at page {find_page(start)} offset {start} table start {last_table_start}"
                    )
                start = min(end - self.section_overlap, start + last_table_start)
            else:
                start = end - self.section_overlap

        if start + self.section_overlap < end:
            yield SplitPage(page_num=find_page(start), text=all_text[start:end])


class TextSplitterBasedOnChapters:
    """
    Class that splits pages into smaller chunks. This is required because embedding models may not be able to analyze an entire page at once
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap  = 200,
            length_function = len,
            is_separator_regex = False,
        )

        # this is created based on the table of contents
        self.chapter_starts = {
            # Personeelszaken
            "Verlof-v1-20230901_101034.pdf": [5, 11, 13, 16, 18, 19, 22, 26, 28, 31, 33, 37, 39, 41, 43],
            "Loon & voordelen-v1-20230901_101018.pdf": [5, 10, 12, 15, 19, 22, 25, 28, 30, 33, 35, 36, 38, 40],
            "Loopbaan-v1-20230901_101001.pdf": [4, 9, 11, 16, 20, 22, 25, 27, 32],
            "Welzijn & gezondheid-v1-20230901_101202.pdf": [6, 8, 12, 19, 32, 34, 36, 38, 40],
            "Loopbaanonderbreking-v1-20230901_101048.pdf": [5, 10, 14, 17, 20, 25, 27, 28, 30],
            "Loon & voordelen-v1-20230901_101018.pdf": [5, 10, 12, 15, 19, 22, 25, 28, 30, 33, 35, 36, 38, 40],
            "Mobiliteit-v1-20230901_101135.pdf": [4, 7, 12, 15, 17, 18],
            "Verzekeringen-v1-20230901_101150.pdf": [4, 13, 17, 19, 21],
            "Dagdienst_ arbeidsduur & registratie-v1-20230901_100856.pdf": [4, 7, 11, 13],
            "Arbeidsreglement, statuut en CAo-v1-20230901_100933.pdf": [4, 5, 6, 7, 8],
            "MyPort-v1-20230901_100948.pdf": [4, 5, 6, 8, 10, 12, 13, 15, 16, 17],
            "Syndicale opdrachten-v1-20230901_101227.pdf": [3,],
            "Personeelsdossier opvragen-v1-20230901_101217.pdf": [3,],
            # Service delivery
            "Helpdesk & interventie-v13-20230904_160207.pdf": [1,],
            "Algemeen-v1-20230901_094814.pdf": [10, 14, 16, 18, 19, 26, 27, 29, 30, 37, 39, 46, 49, 53, 58, 63, 68, 72, 85, 87, 89, 91, 102, 105, 106, 108, 112, 114, 116, 118, 119, 121, 123, 129, 142, 150, 153, 155, 158, 160, 162, 164, 166, 170, 177, 179, 180, 181, 184, 197, 201, 203, 209, ],
            "Mobiel werken - Mobiele WerkPlek-v1-20230901_095100.pdf": [6, 15, 16, 24, 25, 26, 29, 31, 34, 36, 38, 41, 44, 46, 48, 50, 54, 57, 66, 67, 71, 83, 85, 88, 92, 102, 111, 112, 113, 126,],
            "Toepassingen-v2-20230901_095530.pdf": [1,],
            "Interne kb-v1-20230904_163025.pdf": [6, 8, 9, 12, 14, 19, 22, 24, 27, 32, 34, 35, 37, 41, 42, 45, 48, 52, 55, 56, 59, 62, 66, 68, 69, 73, 76, 77, 81, 86, 88, 90, 107, 108, 110, 112, 116, 122, 131, 134, 136, 137, 139, 141, 143, 144, ],
            "Smartphone-v1-20230901_095200.pdf": [5, 6, 9, 15, 27, 31, 32, 40, 41, 44, 56, 61, 62, ],
            "210531-APICS-Barge-Doorklikbare-handleiding-NL.pdf": [1,],
            "e-Balie - handleiding - NL 10.2022.pdf": [4, 5, 8, 9, 24, 33, 35, 40, 45,],
            "Kiosk PC's - Beknopte uitleg-v1-20230901_095019.pdf": [3,],
            "APICS_AL_Help_Versie_1.2.0.pdf": [3, 5, 6, 9, 13, 44, 64, ],
            "Security - Veilig computergebruik-v1-20230901_100240.pdf": [4, 5, 7, 13, 15, 17, 31, 32, 36, 37, 39,],
            "Applicatie-_en_gebruikersbeheer_handleiding_hoofdgebruiker.pdf": [3, 16, ],
            "Applicatie_en_gebruikersbeheer_Handleiding_Gebruiker.pdf": [3, 4, ],
            "Surface Hub-v1-20230901_100203.pdf": [6, 17, 33, ],
            "Service Catalog_ ICT Servicedesk - Core Application Service Desk - toepassingen DI_IN - Overige-v2-20230901_094659.pdf": [1,],
            "Onthaal nieuwe medewerkers - Nuttige informatie betreffende de IT infrastructuur-v1-20230901_094731.pdf": [4, 5, 7, 9, 11, 12, ],
            "Rapportage-v1-20230904_162114.pdf": [4,],
            "Maximo in Microsoft Edge-v1-20230904_161333.pdf": [4,],
            "Activabeheer-v1-20230904_161453.pdf": [5,],
            "Databeheer-v1-20230904_161921.pdf": [4, 8,],
            "Dossierbeheer Averijen-v1-20230904_162134.pdf": [5,],
            "Profiel instellingen-v1-20230904_161356.pdf": [4,],
            "Non conformiteit Maximo.pdf": [2, 4, 5,],
            "Handleiding_Activabeheer.pdf": [3, 5, 11, 12, 13, 15, 19,],
            "SA_Serviceaanvragen_voor_melders.pdf": [2, 4, 6],
            "Beheer Raamovereenkomsten-v1-20230904_161905.pdf": [5, 9, 21],
            "Arbeidsrapportage-v1-20230904_161513.pdf": [5, 20, ],
            "Stappenlijst Port_Dues_Handleiding.pdf": [2, 31,],
            "Planmatig onderhoud-v1-20230904_162058.pdf": [5, 21, 22,],
            "Magazijnbeheer-v1-20230904_161955.pdf": [5, 6, 38, ],
            "Inkoop-v1-20230904_161933.pdf": [7, 9, 16, 32, 92, ],
        }

    def split_pages(self, pages: List[Page], filename: str) -> Generator[SplitPage, None, None]:
       
        # get chapter starts based on file name
        if filename not in self.chapter_starts:
            raise ValueError(f"Filename {filename} not found in dictionary")
        chapter_starts = self.chapter_starts[filename]

        print("Creating chunks for...", filename)

        for idx, chapter_start in enumerate(chapter_starts):
            # get the pages of the chapter
            # we do - 1 since Python indexing starts at 0
            if idx != len(chapter_starts) - 1:
                chapter_end = chapter_starts[idx+1] - 1
                chapter_pages = pages[chapter_start - 1 : chapter_end]
            else:
                chapter_pages = pages[chapter_start - 1 :]
            # first page will be (4, 10)
            # second page will be (10, 12),
            # etc.
            chapter_text = " ".join(page.text for page in chapter_pages)
            # print("---------------")
            # print("Chapter text:", chapter_text)
            # use LangChain's text splitter to create chunks
            for chunk in self.splitter.split_text(chapter_text):
                yield SplitPage(page_num=chapter_start, text=chunk)