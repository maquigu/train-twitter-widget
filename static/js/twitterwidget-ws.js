//JQuery Twitter Feed fed via Websocket
//Based on example by Tom Elliott @ www.webdevdoor.com (2013)

$(document).ready(function () {
    var ws;
    var displaylimit = 30;
    var twitterprofile = "social_west";
    var screenname = "Water Analysts";
    var showdirecttweets = false;
    var showretweets = true;
    var showtweetlinks = true;
    var showprofilepic = true;
    var showtweetactions = true;
    var showretweetindicator = true;
    var openfilter_wss = 'wss://openfilter.co'
    var headerHTML = '';
    var tweetsHTML = '';
    var loadingHTMLOn = 1;
    headerHTML += '<div id = "widget-header">';
    headerHTML += '<div id="bird"><a href="https://twitter.com/" target="_blank"><img src="images/twitter-bird-light.png" width="24" style="float:left;padding:9px 12px 0px 12px" alt="twitter bird" /></a></div>';
    headerHTML += '<div id="of_logo"><a href="https://openfilter.co/" target="_blank"></a></div>';
    headerHTML += '<div id="title-name"><h1>'+screenname+'</h1><span style="font-size:13px;font-style:italic">a list by <a href="https://twitter.com/'+twitterprofile+'" target="_blank">@'+twitterprofile+'</a></span></div>';
    headerHTML += '</div>';
    tweetsHTML += '<div id="tweets-container"><img id="loading-image" src="images/ajax-loader.gif" alt="tweet loader" /></div>';
    
    $('#twitter-feed').html(headerHTML + tweetsHTML);
     
    ws = new WebSocket(openfilter_wss + '/ws-list-feed/openfilter/ca-water-analyst');

    ws.onopen = function(){
        console.log('Connected to Server');
        ws.send(JSON.stringify({'direction': 'new'}));
    };

    ws.onerror = function(ev) { 
        alert('Error '+ev.data);
    };

    ws.onmessage = function(ev) {   
            var message = JSON.parse(ev.data);
            var direction = message['direction'];
            if (message['removed'] == 'OK'){
                $('#of_logo a').css('background-position-x', '0px');
                return;
            }
            console.log('Direction: ' + direction)
            var feeds = message['statuses'];
            console.log('Retrieved ' + feeds.length + ' ' + direction + ' message(s)');
           //alert(feeds);
            var feedHTML = '';
            var displayCounter = 1;         
            for (var i=0; i<feeds.length; i++) {
                var tweetscreenname = feeds[i].user.name;
                var tweetusername = feeds[i].user.screen_name;
                var profileimage = feeds[i].user.profile_image_url_https;
                var status = feeds[i].text; 
                var isaretweet = false;
                var isdirect = false;
                var tweetid = feeds[i].id_str;
                
                //If the tweet has been retweeted, get the profile pic of the tweeter
                if(typeof feeds[i].retweeted_status != 'undefined'){
                   profileimage = feeds[i].retweeted_status.user.profile_image_url_https;
                   tweetscreenname = feeds[i].retweeted_status.user.name;
                   tweetusername = feeds[i].retweeted_status.user.screen_name;
                   tweetid = feeds[i].retweeted_status.id_str;
                   status = feeds[i].retweeted_status.text; 
                   isaretweet = true;
                 };
                 
                 
                 //Check to see if the tweet is a direct message
                 if (feeds[i].text.substr(0,1) == "@") {
                     isdirect = true;
                 }
                 
                //console.log(feeds[i]);
                 
                 //Generate twitter feed HTML based on selected options
                 if (((showretweets == true) || ((isaretweet == false) && (showretweets == false))) && ((showdirecttweets == true) || ((showdirecttweets == false) && (isdirect == false)))) { 
                    if ((feeds[i].text.length > 1) && (displayCounter <= displaylimit)) {             
                        if (showtweetlinks == true) {
                            status = addlinks(status);
                        }

                        feedHTML += '<div class="twitter-article" id="tw'+displayCounter+'">';                                                       
                        feedHTML += '<div class="twitter-pic"><a href="https://twitter.com/'+tweetusername+'" target="_blank"><img src="'+profileimage+'"images/twitter-feed-icon.png" width="42" height="42" alt="twitter icon" /></a></div>';
                        feedHTML += '<div class="twitter-text"><p><span class="tweetprofilelink"><strong><a href="https://twitter.com/'+tweetusername+'" target="_blank">'+tweetscreenname+'</a></strong> <a href="https://twitter.com/'+tweetusername+'" target="_blank">@'+tweetusername+'</a></span><span class="tweet-time"><a href="https://twitter.com/'+tweetusername+'/status/'+tweetid+'" target="_blank">'+relative_time(feeds[i].created_at)+'</a></span><br/>'+status+'</p>';
                        
                        if ((isaretweet == true) && (showretweetindicator == true)) {
                            feedHTML += '<div id="retweet-indicator"></div>';
                        }                       
                        if (showtweetactions == true) {
                            feedHTML += '<div class="twitter-actions"><a class="intent-reply" href="https://twitter.com/intent/tweet?in_reply_to='+tweetid+'" title="Reply"></a><a class="intent-retweet" href="https://twitter.com/intent/retweet?tweet_id='+tweetid+'" title="Retweet"></a><a class="intent-fave" href="https://twitter.com/intent/favorite?tweet_id='+tweetid+'" title="Favourite"></a><a class="intent-remove" id="' + tweetid + '" title="Remove" href="javascript:"></a></div>';
                        }
                        
                        feedHTML += '</div>';
                        feedHTML += '</div>';
                        displayCounter++;
                    }   
                 }
            }
            if (loadingHTMLOn == 1) {
                loadingHTMLOn = 0;
                $('#tweets-container').html('<div id="load-more">Load more ...</div>');
                enableLoadMoreButton();
            }
            if (direction == 'new') {
                //$('#tweets-container').prepend(feedHTML);
                $(feedHTML).hide().prependTo("#tweets-container").fadeIn("slow");
            } else {
                $("#load-more").remove();
                $(feedHTML).hide().appendTo("#tweets-container").fadeIn("slow");
                $('<div id="load-more">Load more ...</div>').hide().appendTo("#tweets-container").fadeIn("slow");
                enableLoadMoreButton();
            }
            //$('#twitter-feed').html(feedHTML);
            
            //Add twitter action animation and rollovers
            if (showtweetactions == true) {             
                $('.twitter-article').hover(function(){
                    $(this).find('.twitter-actions').css({'display':'block', 'opacity':0, 'margin-top':-20});
                    $(this).find('.twitter-actions').animate({'opacity':1, 'margin-top':0},200);
                }, function() {
                    $(this).find('.twitter-actions').animate({'opacity':0, 'margin-top':-20},120, function(){
                        $(this).css('display', 'none');
                    });
                });         
            
                //Add new window for action clicks
            
                $('.intent-reply, .intent-retweet, .intent-fave').click(function(){
                    var url = $(this).attr('href');
                  window.open(url, 'tweet action window', 'width=580,height=500');
                  return false;
                });

                $('.intent-remove').click(function(){
                    ws.send(JSON.stringify({'remove_tweet': $(this).attr('id')}));
                    $(this).closest('.twitter-article').slideUp(250, function(){ $(this).remove() } );
                    $('#of_logo a').css('background-position-x', '-25px');
                });
            }
            
    }
    
    function enableLoadMoreButton() {
        $("#load-more").click(function() {
            console.log('Loading older tweets ...') 
            $(this).css('background-color','#ffce00');
            ws.send(JSON.stringify({'direction': 'old'}));
        });
    }

    //Function modified from Stack Overflow
    function addlinks(data) {
        //Add link to all http:// links within tweets
         data = data.replace(/((https?|s?ftp|ssh)\:\/\/[^"\s\<\>]*[^.,;'">\:\s\<\>\)\]\!])/g, function(url) {
            return '<a href="'+url+'"  target="_blank">'+url+'</a>';
        });
             
        //Add link to @usernames used within tweets
        data = data.replace(/\B@([_a-z0-9]+)/ig, function(reply) {
            return '<a href="http://twitter.com/'+reply.substring(1)+'" style="font-weight:lighter;" target="_blank">'+reply.charAt(0)+reply.substring(1)+'</a>';
        });
        //Add link to #hastags used within tweets
        data = data.replace(/\B#([_a-z0-9]+)/ig, function(reply) {
            return '<a href="https://twitter.com/search?q='+reply.substring(1)+'" style="font-weight:lighter;" target="_blank">'+reply.charAt(0)+reply.substring(1)+'</a>';
        });
        return data;
    }
     
    function relative_time(time_value) {
      var values = time_value.split(" ");
      time_value = values[1] + " " + values[2] + ", " + values[5] + " " + values[3];
      var parsed_date = Date.parse(time_value);
      var relative_to = (arguments.length > 1) ? arguments[1] : new Date();
      var delta = parseInt((relative_to.getTime() - parsed_date) / 1000);
      var shortdate = time_value.substr(4,2) + " " + time_value.substr(0,3);
      delta = delta + (relative_to.getTimezoneOffset() * 60);
     
      if (delta < 60) {
        return '1m';
      } else if(delta < 120) {
        return '1m';
      } else if(delta < (60*60)) {
        return (parseInt(delta / 60)).toString() + 'm';
      } else if(delta < (120*60)) {
        return '1h';
      } else if(delta < (24*60*60)) {
        return (parseInt(delta / 3600)).toString() + 'h';
      } else if(delta < (48*60*60)) {
        //return '1 day';
        return shortdate;
      } else {
        return shortdate;
      }
    }
     
}); 
