---
layout: article
permlink: /contact/
title: "How to get in touch with us"
excerpt: "Details for volunteers, partners and press"
ads: false
share: false

---

You can use this page to get in contact with the team.

If you're looking to volunteer, please fill in [**this google form**](https://docs.google.com/forms/d/1letM0emPYKQ9KP0l37X1GlHO75gSyDwikMB1iVh-V0A/edit). This will allow us to better match your skills to a specific team or problem. We are unable to get back to everyone that applies but will be in contact whenever there is a match between your skills and a specific team.
{: .notice-success}

<br />
<fieldset>
	<form id="contactUs" target="iframecus" action= "https://wh.automate.io/webhook/5ef1ff86c91f9e302c0c1044" method="POST">
		<h2>Contact Form</h2>
		<p>If you wish to get in contact with us, leave a message via the form below. Please fill in all the sections to help us get back to you as quickly as possible.</p>
		<label for="text_field1">Name:</label>
		<input type="text" id="name" name="name" form="contactUs" id="text_field1" />
    <label for="text_field2">Email Address:</label>
		<input type="text" form="contactUs" id="email" name="email" form="contactUs"/>    
		<p>
			<label for="select_element">Which of these options best describes your request</label>
			<select name="purpose" form="contactUs">
					<option value="General">General</option>
					<option value="Partnership">Partnership</option>
					<option value="Press">Press</option>
          <option value="Sponsorship">Sponsorship</option>
			</select>
		</p>
    	<label for="text_area">What is it you'd like to ask?:</label>
		<textarea id="query" name="query" form="contactUs"></textarea>
		<p>
			<input class="btn" type="submit" value="Submit" />
		</p>
	</form>
</fieldset>
<iframe id="iframecus" hidden/>
