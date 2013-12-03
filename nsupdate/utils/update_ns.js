//Global Vars
var oldIP;
var newIP;

function update_ns()
{
var ajaxRequest;

// declare AJAX-Request variable (Browser-dependent)
try{
	// Opera 8.0+, Firefox, Safari
	ajaxRequest = new XMLHttpRequest();
} catch (e){
	// Internet Explorer Browsers
	try{
		ajaxRequest = new ActiveXObject("Msxml2.XMLHTTP");
	} catch (e) {
		try{
			ajaxRequest = new ActiveXObject("Microsoft.XMLHTTP");
		} catch (e){
			// Something went wrong
			alert("Your browser broke!");
			return false;
		}
	}
} 

//Prepare and do the request to get Clients IP from the host
ajaxRequest.open("GET", "https://nsupdate.info/myip", true);
ajaxRequest.send(null); 

// Recieve IP from host
ajaxRequest.onreadystatechange = function(){
	if(ajaxRequest.readyState == 4){
		if(oldIP == '') // Has client IP yet?
		{
			oldIP = ajaxRequest.responseText;
		}
		else
		{
			newIP = ajaxRequest.responseText;
			if(oldIP != newIP) // Has IP changed?
			{
				var update_Request; 
				
				// declare AJAX-Request variable (Browser-dependent)	
				try{
					// Opera 8.0+, Firefox, Safari
					update_Request = new XMLHttpRequest();
				} catch (e){
					// Internet Explorer Browsers
					try{
						update_Request = new ActiveXObject("Msxml2.XMLHTTP");
					} catch (e) {
						try{
							update_Request = new ActiveXObject("Microsoft.XMLHTTP");
						} catch (e){
							// Something went wrong
							alert("Your browser broke!");
							return false;
						}
					}
				}
				
				//Prepare and do the request to update the IP at the host
				update_Request.open("GET", "https://fqdn:secret@nsupdate.info/nic/update", true); // FQDN, SECRET hardcoded here
				update_Request.send(null);
				oldIP == newIP; //Remeber the new IP
			}
		}
	}
}

setTimeout('update_ns()', 300000); //Check again in 5 Minutes (300k millis)
}
