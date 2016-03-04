var page = require('webpage').create();
page.open('http://www.next.co.uk/g31436s3#149855 ');
page.settings.javascriptEnabled=true;
page.onLoadFinished=function(status){
setTimeout(function(){console.log(page.content);phantom.exit()},2000);
};
