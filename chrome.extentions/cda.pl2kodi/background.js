// Called when the user clicks on the browser action.
chrome.browserAction.onClicked.addListener(function(tab) {
  // Send a message to the active tab
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    var activeTab = tabs[0];
	var videolink = tabs[0].url;
	var valid_video ="http://www.cda.pl/video"
	//var addonid="plugin.video.phantom.film";
	var addonid="plugin.video.cdapl";
	
	chrome.storage.sync.get({
        'api_key': '','host': '', 'port': ''
    },
    function(items){
        var api_key = items.api_key;
		var host = items.host;
		var port = items.port;
		
		var url = "http://"+host+":"+port+"/jsonrpc?"
		var request = "request={\"jsonrpc\":\"2.0\",\"method\":\"Addons.ExecuteAddon\",\"params\":{\"addonid\":\""+addonid+"\",\"params\":[\"mode=play\",\"ex_link="+videolink+"\"]},\"id\":1}"
		console.log(videolink);
		console.log(request);
		
		if (host && port && videolink.startsWith(valid_video))
        {
            //chrome.tabs.create({"url": url+request})    
			var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
			xmlhttp.open("GET", url+request);
			xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
			xmlhttp.send();
        }

	});

	console.log("background url tabl = " + tabs[0].url);
	//chrome.tabs.create({"url": tabs[0].url});
    chrome.tabs.sendMessage(activeTab.id, {"message": "clicked_browser_action","url":tabs[0].url});
  });
});


