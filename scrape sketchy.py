import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os
import urllib
import csv
			
main_url = "https://www.sketchymedical.com/courses"
userName = "@gmail.com"
password = ""

img_template = """<img src="%s" />"""
spot_template = """<div class="hotspot" style="left:%s%%;top: %s%%;"></div>"""
sol_template = """<div class="solution" style="left: %s%%;top: %s%%;"> %s </div>"""
driver = webdriver.Firefox()
#driver = webdriver.Chrome()

driver.set_window_size(1000,1000)
wait = WebDriverWait(driver, 10)
driver.get(main_url)
login_button = driver.find_element_by_class_name('login-button')
login_button.click()

element = wait.until(EC.element_to_be_clickable((By.XPATH,"//input[@type='email']")))

time.sleep(1) #this doesn't help. sometimes the password form just won't fill
	
user = driver.find_element_by_xpath("//input[@type='email']")
pass2 = driver.find_element_by_xpath("//input[@type='password']")

user.send_keys(userName)
pass2.send_keys(password)
loginform = driver.find_element_by_class_name('btn-signin')
loginform.click()

element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME,"btn-success")))

def click(driver,object):
	driver.execute_script("return arguments[0].scrollIntoView();", object)
	object.click()
	time.sleep(1)

def cleantxt(string):
	return string.encode('ascii', 'xmlcharrefreplace').strip()
	
def cleanelem(elem):
	return cleantxt(elem.get_attribute("textContent"))

def mktag(string):
	return string.strip().replace(' ','_').lower()
	
def str2fn(string):
	return string.replace("/",",").strip()
	#return "".join([c for c in string if c.isalpha() or c.isdigit() or c==' ']).rstrip()
	
def splittitle(elem):
	chp_header = cleanelem(chapter.find_element_by_tag_name('h2')).split('-')
	chp_num = chp_header[0]
	chp_name = cleantxt("-".join(chp_header[1:]))
	return num, name
	
chapter = ""
with open(os.path.join("output","output_multi.tsv"),'w') as output_file:
	out_multi = csv.writer(output_file,delimiter='\t')
	with open(os.path.join("output","output.tsv"),'w') as output_file:
		out = csv.writer(output_file,delimiter='\t')
		#count the number of buttons. for historical reasons only. not  necessary, could just while until view_buttons[ii] not found. 
		view_buttons = driver.find_elements_by_class_name('btn-success')
		btn_cnt = len(view_buttons)
		for ii in range(btn_cnt):
			view_buttons = driver.find_elements_by_class_name('btn-success')
			btn = view_buttons[ii]
			click(driver,btn)
			#for each section
			section = cleanelem(driver.find_element_by_tag_name('h1'))
			chapters = driver.find_elements_by_class_name('course-chapter')
			for chapter in chapters:
				chp_header = cleanelem(chapter.find_element_by_tag_name('h2')).split('-')
				chp_num = chp_header[0]
				chp_name = cleantxt("-".join(chp_header[1:]))
				review_buttons = chapter.find_elements_by_class_name('btn-review')
				#review_data = chapter.find_elements_by_class_name('litetooltip-hotspot-container')
				for rbtn in review_buttons:
				#for review_html in review_data:
					#print rbtn.get_attribute('disabled')
					if not rbtn.get_attribute('disabled'):
						#wait.until(EC.element_to_be_clickable(rbtn))
						click(driver,rbtn)
						sketch_container = driver.find_element_by_id("review_modal")
						#image_container = sketch_container.find_element_by_class_name("litetooltip-hotspot-container")
						img = sketch_container.find_element_by_tag_name('img')
						dh = img.get_attribute("data-height")
						dw = img.get_attribute("data-width")
						sketch_header = cleanelem(sketch_container.find_element_by_id('review_modal_title')).split("-")
						sketch_num = sketch_header[0]
						sketch_name = cleantxt("-".join(sketch_header[1:]))
						tags = 'sketchy.%s.%s.%s' % (mktag(section), mktag(chp_name), mktag(sketch_name))
						#handle images
						img_src = img.get_attribute("src")
						img_nn = str2fn("%s.jpg" % tags)
						print img_src,img_nn
						img_f = os.path.join('output',img_nn)
						if not os.path.exists(img_f):
							urllib.urlretrieve(img_src,img_f)
						img_html = img_template % img_nn
						#handle hotspots
						hotspots = sketch_container.find_elements_by_class_name('hotspot')
						multi_html = []
						for index,hs in enumerate(hotspots):	
							x = hs.get_attribute('data-hotspot-x')
							y = hs.get_attribute('data-hotspot-y')
							txt = cleanelem(hs.find_element_by_class_name('data-container'))
							spot_html = spot_template % (x, y)
							sol_html = sol_template %  (x, y, txt)
							multi_html += spot_html + sol_html
							title = "%s : %s %s : %s %s" % (section, chp_num, chp_name, sketch_num, sketch_name)
							out.writerow([title,section,chp_num,chp_name,sketch_num,sketch_name,index,img_html,spot_html[-1],sol_html[-1],tags,img_nn,dw,dh,x,y,txt])
						out_multi.writerow([title,section,chp_num,chp_name,sketch_num,sketch_name,img_html,"".join(multi_html),tags])
						#print image_container.get_attribute('innerHTML')
						#container = sketch_container.find_element_by_id("review_modal")
						#print container.get_attribute('innerHTML')
						#wait.until(EC.element_to_be_clickable(close_btn))
						close_btn = sketch_container.find_element_by_class_name("close")
						click(driver,close_btn)
			driver.get(main_url); #this seems dodgy. probably should just get() the main page
			wait.until(EC.element_to_be_clickable((By.CLASS_NAME,"btn-success")))
