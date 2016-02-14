function save_options(){
  var host = document.getElementById('host').value;
  var port = document.getElementById('port').value;

  chrome.storage.sync.set({
	'host': host,
	'port': port,
  },
  function(){
  //  alert('API Key Saved!');
  var status = document.getElementById('status');
  status.textContent = 'Options saved.';
  setTimeout(function() {  status.textContent = ''; }, 750);
  }
  
  );
}


function restore_options(){

  chrome.storage.sync.get({
	'host': '',
	'port': ''
  },
  function(items){
	document.getElementById('host').value = items.host;
	document.getElementById('port').value = items.port;
  });
}

document.addEventListener('DOMContentLoaded', restore_options);
document.getElementById('save').addEventListener('click', save_options);