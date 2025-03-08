import requests
import base64
import json
from datetime import datetime

# API configuration
BASE_URL = "https://api.ed-fi.org/v7.3/api"
TOKEN_ENDPOINT = f"{BASE_URL}/oauth/token"
STUDENTS_ENDPOINT = f"{BASE_URL}/data/v3/ed-fi/students"
COURSE_TRANSCRIPTS_ENDPOINT = f"{BASE_URL}/data/v3/ed-fi/courseTranscripts"

# Replace these with your actual client key, secret, and studentUniqueId
CLIENT_KEY = "RvcohKz9zHI4"
CLIENT_SECRET = "E1iEFusaNf81xzCxwHfbolkC"
STUDENT_UNIQUE_ID = "604822"  # Replace with the desired studentUniqueId

def get_access_token(client_key, client_secret):
    credentials = f"{client_key}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {"grant_type": "client_credentials"}
    
    response = requests.post(TOKEN_ENDPOINT, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to get token: {response.status_code} - {response.text}")

def get_student_by_unique_id(access_token, student_unique_id):
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    params = {"studentUniqueId": student_unique_id}
    response = requests.get(STUDENTS_ENDPOINT, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch student: {response.status_code} - {response.text}")

def get_course_transcripts_count(access_token, student_unique_id):
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    params = {"studentUniqueId": student_unique_id}
    response = requests.get(COURSE_TRANSCRIPTS_ENDPOINT, headers=headers, params=params)
    if response.status_code == 200:
        total_count = response.headers.get("X-Total-Count", len(response.json()))
        return int(total_count)
    else:
        raise Exception(f"Failed to fetch course transcripts count: {response.status_code} - {response.text}")

def get_course_transcripts(access_token, student_unique_id):
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    params = {"studentUniqueId": student_unique_id}
    response = requests.get(COURSE_TRANSCRIPTS_ENDPOINT, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch course transcripts: {response.status_code} - {response.text}")

def transform_data(student, transcripts):
    if not isinstance(student, dict):
        raise ValueError(f"Expected student to be a dict, got {type(student)}: {student}")
    if not isinstance(transcripts, list):
        raise ValueError(f"Expected transcripts to be a list, got {type(transcripts)}: {transcripts}")

    # Base student data
    base_record = {
        "stu_studentaddresscity": "Hometown",
        "_name": "Students",
        "stu_schoolphone": "888-555-1212",
        "stu_studentphone": "888-555-2121",
        "crs_overrideschoolname": "City High School",
        "stu_studentmother": "Unknown",
        "stu_schoolstate": "SC",
        "stu_studentaddress1": "123 Main St",
        "stu_ethnicityrace": student.get("ethnicity", "Unknown"),
        "stu_schoolprincipal": "Unknown",
        "stu_exitdate": "2025",
        "stu_ninthgradecode": "22",
        "stu_schoolcity": "Hometown",
        "stu_schoolassignedid": "1234567890",
        "stu_localschoolstate": "SC",
        "stu_districtname": "Sample School District Five",
        "stu_studentaddresszip": "99999-1234",
        "stu_gradelevel": student.get("gradeLevel", "Unknown"),
        "stu_highschoolname": "City High School",
        "stu_studentfather": "Unknown",
        "stu_birthdate": student.get("birthDate", "Unknown"),
        "stu_uniqueidentifier": student.get("studentUniqueId", "Unknown"),
        "stu_diplomatype": "F",
        "stu_classsize": "500",
        "_id": 10,
        "stu_studentlegalfirstname": student.get("firstName", "Unknown"),
        "stu_classrank": "1",
        "stu_studentenrollmentdate": "2024-08-01",
        "plugin_version": "2019.0.000000.0",
        "stu_gpamax": "10",
        "stu_enrolldate": "2012",
        "stu_localschoolid": "2",
        "stu_studentlevelcode": student.get("gradeLevel", "Unknown"),
        "stu_schooladdress1": "200 Main St",
        "stu_stateassignedid": student.get("stateAssignedId", "9000000000"),
        "stu_schoolzip": "23456-1234",
        "stu_studentlegallastname": student.get("lastSurname", "Unknown"),
        "stu_gpaweighted": "5.000",
        "stu_studentaddressstate": "SC",
        "stu_studentlegalmiddlename": student.get("middleName", ""),
        "stu_academicsummarytype": "Weighted",
        "stu_gpadateranked": "2024-12-31",
        "stu_graduationdate": "2025-05-31",
        "stu_gpaunweighted": "4.000",
        "plugin_sysdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S.0"),
        "stu_graduationyear": "2025",
        "stu_gender": student.get("sex", "Unknown"),
        "stu_studentexitdate": "2025-05-31",
        "stu_diplomalevel": "B18"
    }
    
    # Create a record for each course transcript
    records = []
    for i, transcript in enumerate(transcripts, 1):
        if not isinstance(transcript, dict):
            print(f"Warning: Transcript {i} is not a dict, skipping: {transcript}")
            continue
        
        record = base_record.copy()
        course_ref = transcript.get("courseReference", {})
        record.update({
            "crs_statecoursecode": course_ref.get("courseCode", "Unknown"),
            "crs_statecoursename": transcript.get("courseTitle", "Unknown"),
            "crs_coursecreditvalue": str(transcript.get("attemptedCredits", {}).get("credit", "1") if isinstance(transcript.get("attemptedCredits"), dict) else transcript.get("attemptedCredits", "1")),
            "crs_creditamountearned": str(transcript.get("earnedCredits", {}).get("credit", "1") if isinstance(transcript.get("earnedCredits"), dict) else transcript.get("earnedCredits", "1")),
            "crs_coursegradeearned": str(transcript.get("finalNumericGradeEarned", "Unknown")),
            "crs_coursebegindate": transcript.get("courseAttemptResultDescriptor", {}).get("effectiveBeginDate", "Unknown") if isinstance(transcript.get("courseAttemptResultDescriptor"), dict) else "Unknown",
            "crs_courseenddate": transcript.get("courseAttemptResultDescriptor", {}).get("effectiveEndDate", "Unknown") if isinstance(transcript.get("courseAttemptResultDescriptor"), dict) else "Unknown",
            "crs_sessionname": "S" + str(i),
            "crs_schoolyear": "2021-2022",
            "crs_sessiondesignator": f"2022-0{i}",
            "crs_studentgradelevel": student.get("gradeLevel", "Unknown"),
            "crs_gpaapplicabilitycode": "Applicable",
            "crs_coursecreditbasis": "Regular",
            "crs_qualitypointsearned": "4.3",
            "_id": i
        })
        records.append(record)
    
    return {"name": "Students", "record": records}

def main():
    try:
        # Step 1: Get the access token
        access_token = get_access_token(CLIENT_KEY, CLIENT_SECRET)
        print("Access token obtained successfully.")

        # Step 2: Fetch student by studentUniqueId
        students = get_student_by_unique_id(access_token, STUDENT_UNIQUE_ID)
        # print(f"Raw students response: {json.dumps(students, indent=2)}")  # Debug output
        if not students or not isinstance(students, list) or not students[0]:
            print(f"No valid student data found for studentUniqueId: {STUDENT_UNIQUE_ID}")
            return
        student = students[0]  # Take first match

        # Step 3: Get course transcripts count
        transcript_count = get_course_transcripts_count(access_token, STUDENT_UNIQUE_ID)
        print(f"Total number of course transcripts: {transcript_count}")

        # Step 4: Fetch course transcripts
        transcripts = get_course_transcripts(access_token, STUDENT_UNIQUE_ID)
        # print(f"Raw transcripts response: {json.dumps(transcripts, indent=2)}")  # Debug output
        if not transcripts:
            print(f"No course transcripts found for studentUniqueId: {STUDENT_UNIQUE_ID}")
            return

        # Step 5: Transform and output as JSON
        output_data = transform_data(student, transcripts)
        json_output = json.dumps(output_data, indent=4)
        #print("\nCourse Transcripts Data in JSON format:")
        #print(json_output)

        # Save to file
        with open("course_transcripts_output.json", "w") as f:
            f.write(json_output)
        print("\nData saved to course_transcripts_output.json")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

""" import requests
import base64
import json
from datetime import datetime

# API configuration
BASE_URL = "https://api.ed-fi.org/v7.3/api"
TOKEN_ENDPOINT = f"{BASE_URL}/oauth/token"
STUDENTS_ENDPOINT = f"{BASE_URL}/data/v3/ed-fi/students"
COURSE_TRANSCRIPTS_ENDPOINT = f"{BASE_URL}/data/v3/ed-fi/courseTranscripts"

# Replace these with your actual client key, secret, and studentUniqueId
CLIENT_KEY = "RvcohKz9zHI4"
CLIENT_SECRET = "E1iEFusaNf81xzCxwHfbolkC"
STUDENT_UNIQUE_ID = "604822"  # Replace with the desired studentUniqueId

def get_access_token(client_key, client_secret):
    credentials = f"{client_key}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {"grant_type": "client_credentials"}
    
    response = requests.post(TOKEN_ENDPOINT, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to get token: {response.status_code} - {response.text}")

def get_student_by_unique_id(access_token, student_unique_id):
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    params = {"studentUniqueId": student_unique_id}
    response = requests.get(STUDENTS_ENDPOINT, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch student: {response.status_code} - {response.text}")

def get_course_transcripts_count(access_token, student_unique_id):
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    params = {"studentUniqueId": student_unique_id, "totalCount": "true"}  # Attempt to use totalCount param
    response = requests.get(COURSE_TRANSCRIPTS_ENDPOINT, headers=headers, params=params)
    if response.status_code == 200:
        # Check for totalCount in headers (common Ed-Fi pattern)
        total_count = response.headers.get("X-Total-Count", "Unknown")
        if total_count == "Unknown":
            # Fallback: Count items in response if header not present
            total_count = len(response.json())
        return int(total_count)
    else:
        raise Exception(f"Failed to fetch course transcripts count: {response.status_code} - {response.text}")

def get_course_transcripts(access_token, student_unique_id):
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    params = {"studentUniqueId": student_unique_id}
    response = requests.get(COURSE_TRANSCRIPTS_ENDPOINT, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch course transcripts: {response.status_code} - {response.text}")

def transform_data(student, transcripts):
    # Base student data
    base_record = {
        "stu_studentaddresscity": "Hometown",
        "_name": "Students",
        "stu_schoolphone": "888-555-1212",
        "stu_studentphone": "888-555-2121",
        "crs_overrideschoolname": "City High School",
        "stu_studentmother": "Unknown",
        "stu_schoolstate": "SC",
        "stu_studentaddress1": "123 Main St",
        "stu_ethnicityrace": student.get("ethnicity", "Unknown"),
        "stu_schoolprincipal": "Unknown",
        "stu_exitdate": "2025",
        "stu_ninthgradecode": "22",
        "stu_schoolcity": "Hometown",
        "stu_schoolassignedid": "1234567890",
        "stu_localschoolstate": "SC",
        "stu_districtname": "Sample School District Five",
        "stu_studentaddresszip": "99999-1234",
        "stu_gradelevel": student.get("gradeLevel", "Unknown"),
        "stu_highschoolname": "City High School",
        "stu_studentfather": "Unknown",
        "stu_birthdate": student["birthDate"],
        "stu_uniqueidentifier": student["studentUniqueId"],
        "stu_diplomatype": "F",
        "stu_classsize": "500",
        "_id": 10,
        "stu_studentlegalfirstname": student["firstName"],
        "stu_classrank": "1",
        "stu_studentenrollmentdate": "2024-08-01",
        "plugin_version": "2019.0.000000.0",
        "stu_gpamax": "10",
        "stu_enrolldate": "2012",
        "stu_localschoolid": "2",
        "stu_studentlevelcode": student.get("gradeLevel", "Unknown"),
        "stu_schooladdress1": "200 Main St",
        "stu_stateassignedid": student.get("stateAssignedId", "9000000000"),
        "stu_schoolzip": "23456-1234",
        "stu_studentlegallastname": student["lastSurname"],
        "stu_gpaweighted": "5.000",
        "stu_studentaddressstate": "SC",
        "stu_studentlegalmiddlename": student.get("middleName", ""),
        "stu_academicsummarytype": "Weighted",
        "stu_gpadateranked": "2024-12-31",
        "stu_graduationdate": "2025-05-31",
        "stu_gpaunweighted": "4.000",
        "plugin_sysdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S.0"),
        "stu_graduationyear": "2025",
        "stu_gender": student.get("sex", "Unknown"),
        "stu_studentexitdate": "2025-05-31",
        "stu_diplomalevel": "B18"
    }
    
    # Create a record for each course transcript
    records = []
    for i, transcript in enumerate(transcripts, 1):
        record = base_record.copy()  # Copy base student data
        record.update({
            "crs_statecoursecode": transcript["courseReference"]["courseCode"],
            "crs_statecoursename": transcript.get("courseTitle", "Unknown"),
            "crs_coursecreditvalue": str(transcript.get("attemptedCredits", {}).get("credit", "1")),
            "crs_creditamountearned": str(transcript.get("earnedCredits", {}).get("credit", "1")),
            "crs_coursegradeearned": str(transcript.get("finalNumericGradeEarned", "Unknown")),
            "crs_coursebegindate": transcript.get("courseAttemptResultDescriptor", {}).get("effectiveBeginDate", "Unknown"),
            "crs_courseenddate": transcript.get("courseAttemptResultDescriptor", {}).get("effectiveEndDate", "Unknown"),
            "crs_sessionname": "S" + str(i),  # Placeholder, no direct session mapping
            "crs_schoolyear": "2021-2022",  # Placeholder
            "crs_sessiondesignator": f"2022-0{i}",
            "crs_studentgradelevel": student.get("gradeLevel", "Unknown"),
            "crs_gpaapplicabilitycode": "Applicable",
            "crs_coursecreditbasis": "Regular",
            "crs_qualitypointsearned": "4.3",  # Placeholder
            "_id": i  # Unique ID for each record
        })
        records.append(record)
    
    return {"name": "Students", "record": records}

def main():
    try:
        # Step 1: Get the access token
        access_token = get_access_token(CLIENT_KEY, CLIENT_SECRET)
        print("Access token obtained successfully.")

        # Step 2: Fetch student by studentUniqueId
        students = get_student_by_unique_id(access_token, STUDENT_UNIQUE_ID)
        if not students:
            print(f"No student found with studentUniqueId: {STUDENT_UNIQUE_ID}")
            return
        student = students[0]  # Take first match

        # Step 3: Get course transcripts count
        transcript_count = get_course_transcripts_count(access_token, STUDENT_UNIQUE_ID)
        print(f"Total number of course transcripts: {transcript_count}")

        # Step 4: Fetch course transcripts
        transcripts = get_course_transcripts(access_token, STUDENT_UNIQUE_ID)
        if not transcripts:
            print(f"No course transcripts found for studentUniqueId: {STUDENT_UNIQUE_ID}")
            return

        # Step 5: Transform and output as JSON
        output_data = transform_data(student, transcripts)
        json_output = json.dumps(output_data, indent=4)
        print("\nCourse Transcripts Data in JSON format:")
        print(json_output)

        # Save to file
        with open("course_transcripts_output.json", "w") as f:
            f.write(json_output)
        print("\nData saved to course_transcripts_output.json")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
 """

""" import requests
import base64
import json
from datetime import datetime

# API configuration
BASE_URL = "https://api.ed-fi.org/v7.3/api"
TOKEN_ENDPOINT = f"{BASE_URL}/oauth/token"
STUDENTS_ENDPOINT = f"{BASE_URL}/data/v3/ed-fi/students"

# Replace these with your actual client key, secret, and studentUniqueId
CLIENT_KEY = "RvcohKz9zHI4"
CLIENT_SECRET = "E1iEFusaNf81xzCxwHfbolkC"
STUDENT_UNIQUE_ID = "604822"  # Replace with the desired studentUniqueId

def get_access_token(client_key, client_secret):
    credentials = f"{client_key}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {"grant_type": "client_credentials"}
    
    response = requests.post(TOKEN_ENDPOINT, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to get token: {response.status_code} - {response.text}")

def get_student_by_unique_id(access_token, student_unique_id):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    # Assuming the API supports filtering by studentUniqueId as a query parameter
    params = {"studentUniqueId": student_unique_id}
    
    response = requests.get(STUDENTS_ENDPOINT, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch student: {response.status_code} - {response.text}")

def transform_student_data(student):
    # Map available Ed-Fi fields to the desired format
    full_name = f"{student['firstName']} {student['lastSurname']}"
    record = {
        "stu_studentaddresscity": "Hometown",  # Placeholder
        "_name": "Students",
        "stu_schoolphone": "888-555-1212",  # Placeholder
        "stu_studentphone": "888-555-2121",  # Placeholder
        "crs_overrideschoolname": "City High School",  # Placeholder
        "stu_studentmother": "Unknown",  # Placeholder
        "stu_schoolstate": "SC",  # Placeholder
        "stu_studentaddress1": "123 Main St",  # Placeholder
        "stu_ethnicityrace": student.get("ethnicity", "Unknown"),  # Optional field in schema
        "stu_schoolprincipal": "Unknown",  # Placeholder
        "stu_exitdate": "2025",  # Placeholder
        "stu_ninthgradecode": "22",  # Placeholder
        "stu_schoolcity": "Hometown",  # Placeholder
        "stu_schoolassignedid": "1234567890",  # Placeholder
        "stu_localschoolstate": "SC",  # Placeholder
        "stu_districtname": "Sample School District Five",  # Placeholder
        "crs_statecoursename": "English 1",  # Placeholder
        "crs_gpaapplicabilitycode": "Applicable",  # Placeholder
        "stu_studentaddresszip": "99999-1234",  # Placeholder
        "stu_gradelevel": student.get("gradeLevel", "Unknown"),  # Optional field
        "stu_highschoolname": "City High School",  # Placeholder
        "crs_coursecreditbasis": "Regular",  # Placeholder
        "stu_studentfather": "Unknown",  # Placeholder
        "crs_creditamountearned": "1",  # Placeholder
        "stu_birthdate": student["birthDate"],
        "stu_uniqueidentifier": student["studentUniqueId"],
        "stu_diplomatype": "F",  # Placeholder
        "stu_classsize": "500",  # Placeholder
        "_id": 10,  # Placeholder
        "stu_studentlegalfirstname": student["firstName"],
        "stu_classrank": "1",  # Placeholder
        "stu_studentenrollmentdate": "2024-08-01",  # Placeholder
        "plugin_version": "2019.0.000000.0",  # Placeholder
        "stu_gpamax": "10",  # Placeholder
        "crs_qualitypointsearned": "4.3",  # Placeholder
        "stu_enrolldate": "2012",  # Placeholder
        "stu_localschoolid": "2",  # Placeholder
        "crs_statecoursecode": "302400CW",  # Placeholder
        "stu_studentlevelcode": student.get("gradeLevel", "Unknown"),  # Optional field
        "crs_schoolyear": "2021-2022",  # Placeholder
        "crs_courseenddate": "2022-06-02",  # Placeholder
        "crs_studentgradelevel": "NinthGrade",  # Placeholder
        "crs_sessiondesignator": "2022-01",  # Placeholder
        "stu_schooladdress1": "200 Main St",  # Placeholder
        "stu_stateassignedid": student.get("stateAssignedId", "9000000000"),  # Optional field
        "crs_coursegradeearned": "93",  # Placeholder
        "stu_schoolzip": "23456-1234",  # Placeholder
        "crs_coursebegindate": "2022-01-13",  # Placeholder
        "stu_studentlegallastname": student["lastSurname"],
        "stu_gpaweighted": "5.000",  # Placeholder
        "crs_sessionname": "S2",  # Placeholder
        "stu_studentaddressstate": "SC",  # Placeholder
        "stu_studentlegalmiddlename": student.get("middleName", ""),  # Optional field
        "stu_academicsummarytype": "Weighted",  # Placeholder
        "stu_gpadateranked": "2024-12-31",  # Placeholder
        "stu_graduationdate": "2025-05-31",  # Placeholder
        "stu_gpaunweighted": "4.000",  # Placeholder
        "plugin_sysdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S.0"),
        "stu_graduationyear": "2025",  # Placeholder
        "stu_gender": student.get("sex", "Unknown"),  # Optional field
        "stu_studentexitdate": "2025-05-31",  # Placeholder
        "crs_coursecreditvalue": "1",  # Placeholder
        "stu_diplomalevel": "B18"  # Placeholder
    }
    return {
        "name": "Students",
        "record": [record]
    }

def main():
    try:
        # Step 1: Get the access token
        access_token = get_access_token(CLIENT_KEY, CLIENT_SECRET)
        print("Access token obtained successfully.")

        # Step 2: Fetch student by studentUniqueId
        students = get_student_by_unique_id(access_token, STUDENT_UNIQUE_ID)
        if not students:
            print(f"No student found with studentUniqueId: {STUDENT_UNIQUE_ID}")
            return

        # Step 3: Transform and output as JSON
        student_data = transform_student_data(students[0])  # Assuming first match
        json_output = json.dumps(student_data, indent=4)
        print("\nStudent Data in JSON format:")
        print(json_output)

        # Optionally save to file
        with open("student_output.json", "w") as f:
            f.write(json_output)
        print("\nData saved to student_output.json")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
 """



""" 
V1
import requests
import base64

# API configuration
BASE_URL = "https://api.ed-fi.org/v7.3/api"
TOKEN_ENDPOINT = f"{BASE_URL}/oauth/token"
STUDENTS_ENDPOINT = f"{BASE_URL}/data/v3/ed-fi/students"

# Replace these with your actual client key and secret
CLIENT_KEY = "RvcohKz9zHI4"
CLIENT_SECRET = "E1iEFusaNf81xzCxwHfbolkC"

def get_access_token(client_key, client_secret):
    # Prepare the Authorization header: Base64 encode "client_key:client_secret"
    credentials = f"{client_key}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "grant_type": "client_credentials"
    }
    
    # Request the token
    response = requests.post(TOKEN_ENDPOINT, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to get token: {response.status_code} - {response.text}")

def get_students(access_token):
    # Use the token to authenticate the request to the students endpoint
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    # Fetch students
    response = requests.get(STUDENTS_ENDPOINT, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch students: {response.status_code} - {response.text}")

def main():
    try:
        # Step 1: Get the access token
        access_token = get_access_token(CLIENT_KEY, CLIENT_SECRET)
        print("Access token obtained successfully.")

        # Step 2: Fetch students
        students = get_students(access_token)
        
        # Step 3: Extract and display name and birth date
        print("\nStudent Data:")
        for student in students:
            full_name = f"{student['firstName']} {student['lastSurname']}"
            birth_date = student['birthDate']
            print(f"Name: {full_name}, Date of Birth: {birth_date}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() """