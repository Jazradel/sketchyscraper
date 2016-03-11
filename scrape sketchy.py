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
userName = "jameslkau@gmail.com"
password = "skejKil0"

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

time.sleep(0.5) #this doesn't help. sometimes the password form just won't fill
	
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

def cleantxt(elem):
	return elem.get_attribute("textContent").encode('ascii', 'xmlcharrefreplace').strip()

def str2fn(string):
	return string.replace("/",",").strip()
	#return "".join([c for c in string if c.isalpha() or c.isdigit() or c==' ']).rstrip()
	
chapter = ""
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
		section = cleantxt(driver.find_element_by_xpath('//h1'))
		chapters = driver.find_elements_by_class_name('btn-success')
		for chapter in chapters:
			chapter_title = cleantxt(chapter)
			review_buttons = chapter.find_elements_by_class_name('btn-review')
			for rbtn in review_buttons:
				#print rbtn.get_attribute('disabled')
				if not rbtn.get_attribute('disabled'):
					#wait.until(EC.element_to_be_clickable(rbtn))
					click(driver,rbtn)
					image_container = driver.find_element_by_class_name("litetooltip-hotspot-container")
					img = image_container.find_element_by_xpath('//img')
					dh = img.get_attribute("data-height")
					dw = img.get_attribute("data-width")
					name = cleantxt(driver.find_element_by_id('review_modal_title'))
					img_src = img.get_attribute("src")
					img_nn = str2fn("%s.png" % name)
					print img_src,img_nn
					img_f = os.path.join('output',img_nn)
					if not os.path.exists(img_f):
						urllib.urlretrieve(img_src,img_f)
					hotspots = image_container.find_elements_by_class_name('hotspot')
					for index,hs in enumerate(hotspots):	
						x = hs.get_attribute('data-hotspot-x')
						y = hs.get_attribute('data-hotspot-y')
						txt = cleantxt(hs.find_element_by_class_name('data-container'))
						img = img_template % img_nn
						spot = spot_template % (x, y)
						sol = sol_template %  (x, y, txt)
						tags = ''
						out.writerow([section,chapter,name,img,index,spot,sol,tags,img_nn,dh,dy,x,y,txt])
					#print image_container.get_attribute('innerHTML')
					container = driver.find_element_by_id("review_modal")
					#print container.get_attribute('innerHTML')
					#wait.until(EC.element_to_be_clickable(close_btn))
					close_btn = container.find_element_by_class_name("close")
					click(driver,close_btn)
			driver.get(main_url); #this seems dodgy. probably should just get() the main page
			wait.until(EC.element_to_be_clickable((By.CLASS_NAME,"btn-success")))