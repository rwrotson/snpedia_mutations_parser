import random
import json
import csv
from time import sleep

from bs4 import BeautifulSoup
import requests


HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
    }
BASE_URL = 'https://www.snpedia.com'
FIRST_PAGE_URL = 'https://www.snpedia.com/index.php?title=Category:Is_a_gene'
FIRST_PAGE_PATH = 'lists_pages/page_0.html'

CLINVAR_STYLE = 'width:25em; font-size: 90%%; border: 1px solid #aaaaaa; background-color: #f9f9f9; color: black; margin-bottom: 0.5em; margin-left: 1em; padding: 0.2em; float: right; clear: right; text-align:left;'
GWAS_SNP_STYLE = 'width:25em; font-size: 90%; border: 1px solid #aaaaaa; background-color: #f9f9f9; color: black; margin-bottom: 0.5em; margin-left: 1em; padding: 0.2em; float: right; clear: right; text-align:left;'
MERGED_STYLE = 'background-color: #FFC0C0; width:90%;'

CLINVAR_URL = 'https://www.snpedia.com/index.php/Rs8150'
GWAS_SNP_URL = 'https://www.snpedia.com/index.php/Rs2515629'
MERGED_URL = 'https://www.snpedia.com/index.php/Rs4149313'


def download_first_page(url):
    
    req = requests.get(url, HEADERS)

    with open(FIRST_PAGE_PATH, 'w') as file:
        file.write(req.text)

    print('#' * 40)
    print('FIRST PAGE WAS SUCCESSFULLY DOWNLOADED!')


def download_lists_pages():
    """
    Download all pages with lists of genes into '/list_pages/' directory
    """

    for i in range(0, 11):
        with open(f'lists_pages/page_{i}.html', 'r') as file:
            soup = BeautifulSoup(file, 'lxml')

        try:
            next_page = BASE_URL + soup.find('a', string='next page').get('href')
        except AttributeError:
            print('All pages were downloaded')
            break

        with open('txt_lists/pages.txt', 'a') as pages:
            pages.write(next_page + '\n')

        req = requests.get(next_page, HEADERS)
        with open(f'lists_pages/page_{i + 1}.html', 'w') as file:
            file.write(req.text)

    print('#' * 40)
    print('ALL GENES PAGES WAS SUCCESSFULLY DOWNLOADED!\n')


def get_genes_links():
    """
    Find all links to genes pages and save it to genes.txt
    """

    count = 0

    for i in range(0, 11):
        with open(f'lists_pages/page_{i}.html', 'r') as file:
            soup = BeautifulSoup(file, 'lxml')
        genes_groups = soup.find_all(class_='mw-category-group')

        print(f'Found {len(genes_groups)} on page {i}')

        for gene_group in genes_groups:
            genes_list = gene_group.find_all('li')

            for gene in genes_list:
                with open('txt_lists/genes.txt', 'a') as genes:
                    genes.write(BASE_URL + '/index.php/' + gene.text)
                    genes.write('\n')

            count += len(genes_list)
            print(f'Found {len(genes_list)} more genes')
            print(f'Found {count} genes')

    print('#' * 40)
    if count == 2162:
        print('ALL GENES HAVE BEEN FOUND SUCCESSFULLY!\n')
    else:
        print('NOT ALL GENES HAVE BEEN FOUND\n')


def get_mutations_links(start_from):
    """
    Find all links to mutation pages and save it to
    mutations.txt and to mutations.json
    """

    total_count = 0
    iterations_left = 2162

    with open('txt_lists/genes.txt', 'r') as file:
        genes_links = file.readlines()
    genes_links = [link.rstrip() for link in genes_links]

    for link in genes_links:
        title = link.split('/')[-1]
        req = requests.get(link, HEADERS)
        soup = BeautifulSoup(req.text, 'lxml')
        mutations_table = soup.find('table', class_='wikitable')
        try:
            mutations_tds = mutations_table.find_all('td', class_='smwtype_wpg')
        except AttributeError:
            print(f'0 mutations for gene {title} added')
            print('Moving on to the next iteration...')
            iterations_left -= 1
            print(f'{iterations_left} iterations left')
            print('...')
            sleep(random.randrange(2, 4))
            continue

        mutations_list = []

        for td in mutations_tds:
            mutation_id = td.contents[0].text
            mutation_link = td.contents[0].get('href')
            mutations_list.append(mutation_id)

            with open('txt_lists/mutations.txt', 'a') as mutations:
                mutations.write(BASE_URL + mutation_link + '\n')

        mutations_dict = {
            'gene': title,
            'mutations': mutations_list
        }
        with open('json/mutations.json', 'a') as json_file:
            json.dump(mutations_dict, json_file, indent=4)

        iteration_count = len(mutations_tds)
        total_count += iteration_count
        iterations_left -= 1

        print(f'{iteration_count} mutations for gene {title} added')
        print(f'{total_count} mutations added total')
        print(f'{iterations_left} iterations left')
        print('...')

        sleep(random.randrange(2, 4))

    print('#' * 40)
    print('ALL MUTATIONS COLLECTED SUCCESSFULLY')
    print(f'{total_count} MUTATIONS COLLECTED\n')


def delete_doubles(path_to_file):
    """
    Delete dublicate lines in file and save it to copy
    """
    with open(path_to_file, 'r') as file:
        lines = file.readlines()
    lines_set = set(lines)
    name, ext = path_to_file.split('.') 
    with open(f'{name}_wo_doubles.{ext}', 'w') as file:
        for line in lines_set:
            file.write(line)


def get_csv_headers(url, csvfile, style):
    """
    Find all links to mutation pages and save it to
    mutations.txt and to mutations.json
    """

    req = requests.get(url, HEADERS)
    soup = BeautifulSoup(req.text, 'lxml')

    mutations_table = soup.find('table', {'style': style})
    mutations_trs = mutations_table.find_all('tr')[1:]
    csv_row = ['mutation']
    for tr in mutations_trs:
        csv_row.append(tr.th.text.strip())

    with open(f'csv/{csvfile}.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(csv_row)

    print('#' * 40)
    print(f'HEADERS TO {csvfile.upper()}.CSV CREATED SUCCESSFULLY!\n')


def get_merged_headers():
    with open('csv/merged.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['from', 'into'])

    print('#' * 40)
    print('HEADERS TO MERGED.CSV CREATED SUCCESSFULLY!\n')


def get_clinvar_info(title, soup):
    """
    Find clinvar table and write it down into clinvar.csv
    """
    table = soup.find('table', {'style': CLINVAR_STYLE})
    if table is None:
        print(f'Clinvar table for {title} not found')
        return None

    mutations_trs = table.find_all('tr')[1:]
    csv_row = [title]

    for tr in mutations_trs:
        if tr.td.find_all('a') == []:
            tr_text = tr.td.text.strip()
            csv_row.append(tr_text)
        else:
            csv_a_row = ''
            for a in tr.td.find_all('a'):
                tr_text = a.text
                if a.get('class') == ['new']:
                    csv_a_row += f'{tr_text}; '
                else:
                    tr_href = a.get('href')
                    if tr_href[0] == '/':
                        tr_href = BASE_URL + tr_href
                    csv_a_row += f'{tr_text} [{tr_href}]; '
            csv_row.append(csv_a_row[:-2])

    with open('csv/clinvar.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow(csv_row)

    print(f'Clinvar values for {title} successfully added')


def get_gwas_snp_info(title, soup):
    """
    Find gwas snp tables and write it down into gwas_snp.csv
    """
    tables = soup.find_all('table', {'style': GWAS_SNP_STYLE})
    if tables == []:
        print(f'GWAS snp tables for {title} not found')
        return None

    for table in tables:
        if table.find('big').text.strip() != 'GWAS snp':
            continue
        mutations_trs = table.find_all('tr')[1:]

        pmid = mutations_trs[0]
        pmid_href = pmid.td.contents[1].get('href')
        csv_row = [title, pmid_href]

        mutations_trs = mutations_trs[1:]

        for tr in mutations_trs:
            if tr.td.find_all('a') == []:
                tr_text = tr.td.text.strip()
            else:
                tr_text = tr.td.a.text
            csv_row.append(tr_text)
    try:
        with open('csv/gwas_snp.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerow(csv_row)
    except UnboundLocalError:
        pass

    print(f'{len(tables)} GWAS snp values for {title} successfully added')


def get_merged_info(title, soup):
    """
    Check if mutation was renamed and find its new title
    """
    table = soup.find('table', {'style': MERGED_STYLE})
    if table is None:
        print('No merges')
        return None

    merged_into = table.tr.contents[1].find('a').get('title')
    csv_row = [title, merged_into]

    with open('csv/merged.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow(csv_row)

    print(f'{title} was merged into {merged_into}')


def get_mutations_info(start_from=0):
    """
    Write all relevant info about mutations into csv files
    """

    with open('txt_lists/mutations_wo_doubles.txt', 'r') as mutations:
        mutations_links = mutations.readlines()[start_from:]
    mutations_links = [link.rstrip() for link in mutations_links]

    iterations_left = len(mutations_links)
    count_pointer = start_from

    for link in mutations_links:

        try:
            req = requests.get(link, HEADERS)
        except requests.exceptions.ConnectionError:
            print('CONNECTION ERROR!')
            print(f'On {count_pointer} line of mutations.txt')
            print('Trying to reconnect...\n')
            
            sleep(random.randrange(10, 20))
            get_mutations_info(count_pointer)
            return None

        title = link.split('/')[-1]
        soup = BeautifulSoup(req.text, 'lxml')

        get_clinvar_info(title, soup)
        get_gwas_snp_info(title, soup)
        get_merged_info(title, soup)

        count_pointer += 1

        iterations_left -= 1
        print(f'{iterations_left} iterations left')
        print('...')

        sleep(random.randrange(2, 4))

    print('#' * 40)
    print('ALL MUTATIONS INFO SUCCESSFULLY COLLECTED!\n')


def main():
    download_first_page(FIRST_PAGE_URL)
    download_lists_pages()

    get_genes_links()
    get_mutations_links(0)
    delete_doubles('txt_lists/mutations.txt')

    get_csv_headers(CLINVAR_URL, 'clinvar', CLINVAR_STYLE)
    get_csv_headers(GWAS_SNP_URL, 'gwas_snp', GWAS_SNP_STYLE)
    get_merged_headers()

    get_mutations_info()

if __name__ == '__main__':
    main()
