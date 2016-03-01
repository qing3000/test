var page = require('webpage').create();
page.open('http://www.next.co.uk/x57794s9');
page.settings.javascriptEnabled=true;
page.onLoadFinished=function(status){
setTimeout(function(){console.log(page.content);phantom.exit()},2000);
};
