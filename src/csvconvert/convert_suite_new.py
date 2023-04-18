import os
import csv
from xml.dom.minidom import Document

# 실행 파일의 디렉토리 경로
base_dir = os.path.dirname(os.path.abspath(__file__))

# CSV 파일 디렉토리 경로
csv_dir = os.path.join(base_dir, 'Testsuite', 'CSV')

# XML 파일 디렉토리 경로
xml_dir = os.path.join(base_dir, 'Testsuite', 'XML')

# 줄바꿈 문자를 <br> 태그로 변환하는 함수
def newline_to_br(text):
    return text.replace('\n', '<br>')

# CSV 파일 목록 가져오기
csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

# CSV 파일 목록 출력
print("CSV 파일 목록:")
for i, csv_file in enumerate(csv_files):
    print(f"{i+1}. {csv_file}")

# 사용자로부터 CSV 파일 선택
csv_index = int(input("변환할 CSV 파일 번호를 입력하세요: ")) - 1
csv_file = csv_files[csv_index]

# XML 파일 이름 생성
xml_name = os.path.splitext(csv_file)[0] + ".xml"
xml_path_template = os.path.join(xml_dir, xml_name[:-4] + "-{}.xml")

# 각 테스트케이스의 단계 번호를 추적하기 위한 딕셔너리
step_counter = {}

# 중복된 파일명 처리
if os.path.exists(xml_path_template.format(1)):
    i = 1
    while True:
        if not os.path.exists(xml_path_template.format(i)):
            break
        i += 1
    xml_path_template = os.path.join(xml_dir, xml_name[:-4] + "-{{}}_{}.xml".format(i))

doc = Document()
root = doc.createElement('testsuite')
doc.appendChild(root)

with open(os.path.join(csv_dir, csv_file), 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    header = next(csvreader)
    suite_name = ''
    count = 0
    for row in csvreader:
        if count % 200 == 0:
            # XML 파일 저장
            if count > 0:
                with open(xml_path, 'w', encoding='utf-8') as xmlfile:
                    xmlfile.write(doc.toprettyxml(indent='  ', newl='\n'))
                print(f"XML 파일이 {xml_path}로 변환되었습니다.")
            # XML 파일 이름 변경
            xml_path = xml_path_template.format(count//200 + 1)
            doc = Document()
            root = doc.createElement('testsuite')
            doc.appendChild(root)
            suite_name = ''
            step_counter.clear()

        if suite_name != row[0]:
            suite_name = row[0]
            suite = doc.createElement('testsuite')
            suite.setAttribute('name', suite_name)
            root.appendChild(suite)
            testcase = None
        if not testcase or testcase.getAttribute('name') != row[1]:
            testcase = doc.createElement('testcase')
            testcase.setAttribute('name', row[1])
            suite.appendChild(testcase)

            # 테스트 케이스의 summary, preconditions 요소 추가
            summary = doc.createElement('summary')
            summary.appendChild(doc.createCDATASection(row[2]))
            testcase.appendChild(summary)

            preconditions = doc.createElement('preconditions')
            preconditions.appendChild(doc.createCDATASection(row[3]))
            testcase.appendChild(preconditions)
                
            # 테스트 케이스의 첫 번째 단계 추가
            step = doc.createElement('step')

            step_number = doc.createElement('step_number')
            step_number.appendChild(doc.createTextNode(str(1)))
            step.appendChild(step_number)

            actions = doc.createElement('actions')
            actions.appendChild(doc.createCDATASection(newline_to_br(row[5])))
            step.appendChild(actions)

            expectedresults = doc.createElement('expectedresults')
            expectedresults.appendChild(doc.createCDATASection(newline_to_br(row[6])))
            step.appendChild(expectedresults)

            steps = doc.createElement('steps')
            steps.appendChild(step)
            testcase.appendChild(steps)

            # step_counter 초기화
            step_counter[testcase.getAttribute('name')] = 2

        else:
            # 이전과 동일한 테스트 케이스일 경우, 마지막 단계의 step_number를 추출하여 +1 해줌
            last_step = steps.getElementsByTagName('step')[-1]
            last_step_number = int(last_step.getElementsByTagName('step_number')[0].firstChild.nodeValue)
            step_number = last_step_number + 1

            # 새로운 단계 추가
            step = doc.createElement('step')

            step_number_node = doc.createElement('step_number')
            step_number_node.appendChild(doc.createTextNode(str(step_number)))
            step.appendChild(step_number_node)

            actions = doc.createElement('actions')
            actions.appendChild(doc.createCDATASection(newline_to_br(row[5])))
            step.appendChild(actions)

            expectedresults = doc.createElement('expectedresults')
            expectedresults.appendChild(doc.createCDATASection(newline_to_br(row[6])))
            step.appendChild(expectedresults)

            steps.appendChild(step)

            # step_counter 갱신
            step_counter[testcase.getAttribute('name')] = step_number

        count += 1

# 마지막 XML 파일 저장
with open(xml_path, 'w', encoding='utf-8') as xmlfile:
    xmlfile.write(doc.toprettyxml(indent='  ', newl='\n'))
print(f"XML 파일이 {xml_path}로 변환되었습니다.")
