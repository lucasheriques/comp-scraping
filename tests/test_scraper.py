import unittest
from bs4 import BeautifulSoup
from comp_scraping.scraper import parse_company_name, parse_location, parse_cell_text, handle_hidden_value, parse_salary_data, get_timestamped_filename

class TestScraperFunctions(unittest.TestCase):

    def test_parse_company_name(self):
        html = '<td><a class="salary-row_companyName__obLh0">Test Company</a></td>'
        soup = BeautifulSoup(html, 'html.parser')
        self.assertEqual(parse_company_name(soup), 'Test Company')

        html = '<td><span class="salary-row_anonymizedCompany__DFcB6">Software Engineer</span></td>'
        soup = BeautifulSoup(html, 'html.parser')
        self.assertEqual(parse_company_name(soup), 'Anonymous')

        html = '<td></td>'
        soup = BeautifulSoup(html, 'html.parser')
        self.assertIsNone(parse_company_name(soup))

    def test_parse_location(self):
        html = '<td><span class="MuiTypography-caption">São Paulo, Brazil | 2 days ago</span></td>'
        soup = BeautifulSoup(html, 'html.parser')
        self.assertEqual(parse_location(soup), 'São Paulo, Brazil')

        html = '<td></td>'
        soup = BeautifulSoup(html, 'html.parser')
        self.assertEqual(parse_location(soup), '')

    def test_parse_cell_text(self):
        html = '<p>Test Text</p>'
        soup = BeautifulSoup(html, 'html.parser')
        self.assertEqual(parse_cell_text(soup), 'Test Text')

        self.assertEqual(parse_cell_text(None), '')

    def test_handle_hidden_value(self):
        self.assertEqual(handle_hidden_value('hidden'), 'N/A')
        self.assertEqual(handle_hidden_value('visible'), 'visible')

    def test_parse_salary_data(self):
        html = '''
        <table>
            <tbody>
                <tr>
                    <td><a class="salary-row_companyName__obLh0">Test Company</a><span class="MuiTypography-caption">São Paulo, Brazil | 2 days ago</span></td>
                    <td><p>Senior</p><span>Software Engineer</span></td>
                    <td><p>5-7 yrs</p><span>3-5 yrs</span></td>
                    <td><p>R$200,000</p><span>150K | 50K | 0</span></td>
                </tr>
            </tbody>
        </table>
        '''
        data = parse_salary_data(html)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['Company'], 'Test Company')
        self.assertEqual(data[0]['Location'], 'São Paulo, Brazil')
        self.assertEqual(data[0]['Level Name'], 'Senior')
        self.assertEqual(data[0]['Role'], 'Software Engineer')
        self.assertEqual(data[0]['Years of Experience'], '5-7 yrs')
        self.assertEqual(data[0]['Years at Company'], '3-5 yrs')
        self.assertEqual(data[0]['Total Compensation'], 'R$200,000')
        self.assertEqual(data[0]['Compensation Breakdown'], '150K | 50K | 0')

if __name__ == '__main__':
    unittest.main()
