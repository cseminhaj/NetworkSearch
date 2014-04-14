var showStructuredSearch = window.location.search.indexOf('showSearch') > 0 
var DEBUG = window.location.search.indexOf('DEBUG') > 0
var showMongo = DEBUG || window.location.search.indexOf('showMongo') > 0
var showRank = DEBUG || window.location.search.indexOf('showRank') > 0 || getCookie('showRank')!= 'false'
var showStructuredSearch = window.location.search.indexOf('showStructure') > 0
var useBox = window.location.search.indexOf('useBox') > 0
var numProjRows = 0
var numMatchRows = 1
var numLinkRows	= 1
var attrSelects = [
	'sort',	
	'aggAttr',
	'by'
]
var adsEnable = false

// Recent searches: constants and an obj to hold current rather than
//  checking cookie all the time
var COOKIE_EXP  = 30
var RECENT  = 'netwsearch_recent'

var isProject = false

// Attributes that should not be displayed with the object
var HIDE_ATTRS = ['object-type', 'result-score']

// Minimum number of letters to type before giving suggestions
var MIN_SUGGESTION_LENGTH = 2

// Maximum number of chars displayed in a value
var MAX_VAL_LENGTH = 100 

// Maximum number of chars in an object name
var MAX_NAME_LENGTH = 94 

// Recent searches: constants and an obj to hold current rather than
//	checking cookie all the time
var COOKIE_EXP	= 30
var RECENT	= 'netwsearch_recent'
//var NUM_SEARCHES= 10
var NUM_SEARCHES= 5
var searches	= {}


$(document).ready(function() {
 	//document.getElementById('max_result').value = 100;
 	//document.getElementById('ebr').value = 5;
 	//document.getElementById('nr').value = 5;
 	//document.getElementById('tr').value = 5;
 	//document.getElementById('hop_limit').value = 10;
 	//var $radios = $('input:radio[name=query_matching]');
    //if($radios.is(':checked') === false) {
    //    $radios.filter('[value=approximate]').prop('checked', true);
    //}
	getSampleQuery()


});

$("#ns_search").click(function(event){
	search()
});

function search(query){
		if (typeof query !== 'undefined'){
			document.nsQuery.search_query.value = query
		}else{
			query = document.nsQuery.search_query.value
		}
		
		//query = typeof query !== 'undefined' ? query :  document.nsQuery.search_query.value;
	 	var max_result = document.nsParameter.max_result.value
	 	var query_matching = $('input[name="query_matching"]:checked').val()
	 	var ebr = document.nsParameter.ebr.value
	 	var nr = document.nsParameter.nr.value
	 	var tr = document.nsParameter.tr.value
		var fs = document.nsParameter.fs.value
		var ms = document.nsParameter.ms.value
		var ds = document.nsParameter.ds.value
	 	var hop_limit = document.nsParameter.hop_limit.value
		var vicinityPrecision = $('input[name="vicinityPrecision"]:checked').val()
	 	if(query_matching == 'approximate'){
	 		approximate = true
	 	}else{
		 	approximate = false
	 	}
		console.dir(vicinityPrecision)
	 	if(vicinityPrecision == 'precise'){
	 		vicinityPrecision = true
	 	}else{
		 	vicinityPrecision = false
	 	}
		console.dir('vicinity======================')
		console.dir(vicinityPrecision)
        document.getElementById('queryResults').innerHTML = ''
		 $('#loadingDisplay').show();

		data = {'query':query, 'parameters':{'limit':max_result, 'isApprox':approximate,
			'tf':ebr,'nr':nr,'tr':tr,'fs':fs,'ms':ms,'ds': ds,'hop':hop_limit,'vicinity-precision': vicinityPrecision}};
		$.ajax({
		    type: "POST",
		    url: "/search",
		    data: JSON.stringify( data ),
		    contentType: "application/json; charset=utf-8",
		    dataType: "json",
		    success: function(data){
		        console.dir(data);
				$('#loadingDisplay').hide();
		        sendQueryResp(data);

		    },
		    failure: function(err) {
				$('#loadingDisplay').hide();
		        alert(err);
	    	}
    	});
}

function getSampleQuery()
{
	$.getJSON( "/sample-query", function( data ) {
		console.dir(data);
		displaySampleQuery(data)
	});
}

function displaySampleQuery(data){
	var queries = data.query
	var html = '' 
	for (i=0;i<queries.length;i++) {
		html += '<a id="'+ name + i +'" class="list-group-item" href="javascript:search(\'' + escape(queries[i]) + '\')">' + shorten(queries[i],100) + '</a>'
	}    
	document.getElementById('sample-query').innerHTML = html 
}

// Ajax response function to display query results
function sendQueryResp(data) {
	var r = data
    window.query = r.mq
	console.dir('recieve data')
	console.dir(data)
	isProject = r.parameters['isProject']
	var items = r.results
	if (items) {
		var metaInfo = ' ' + items.length + ' results (' + r.time.toFixed(3) + ' seconds)' 
		if (showRank && 'rank_time' in r) 
			metaInfo += ' <label class="rank">Rank time ' + r.rank_time.toFixed(0) + ' milliseconds.</label>'
		document.getElementById('queryMeta').innerHTML = metaInfo
		objectResp(items, 'queryResults', getDisplayAttrs(r.query))
	} else {
		document.getElementById('queryResults').innerHTML = 'No matches'
	}
	
	if (showMongo) {
		//document.getElementById('mongo').innerHTML = 'MONGO: ' + r.mongo
		//document.getElementById('mongo').style.display = 'block'
	}
	//document.getElementById('currentSettingLabel').innerHTML =''
	//if (r.parameters['approximate'] != false) {
	//	document.getElementById('currentSettingLabel').innerHTML  += " Approximate matching <p>"
	//	document.getElementById('currentSettingLabel').innerHTML  += " Ranking weights : " 
	//	document.getElementById('currentSettingLabel').innerHTML  += " <ul>" 
	//	document.getElementById('currentSettingLabel').innerHTML  +="<li> EPR : " + r.parameters['tf'] + "</li>"
	//	document.getElementById('currentSettingLabel').innerHTML  +="<li> NR : " + r.parameters['nr'] + "</li>"  
	//	document.getElementById('currentSettingLabel').innerHTML  +="<li> TR : " + r.parameters['tr'] + "</li>" 
	//	document.getElementById('currentSettingLabel').innerHTML  +="<li> FS : " + r.parameters['fs'] + "</li>"  
	//	document.getElementById('currentSettingLabel').innerHTML  +="<li> MS : " + r.parameters['ms'] + "</li>" 
	//	document.getElementById('currentSettingLabel').innerHTML  +="<li> DS : " + r.parameters['ds'] + "</li>" 
	//	document.getElementById('currentSettingLabel').innerHTML  += " <ul>" 
	//	document.getElementById('currentSettingLabel').innerHTML  +="<p> Hop limit : " + r.parameters['hop'] + "</p>"
	//	
	//	if (r.parameters['limit']) 
	//		document.getElementById('currentSettingLabel').innerHTML  += "<p>  Max "+r.parameters['limit']+" results" 
	//	else
	//		document.getElementById('currentSettingLabel').innerHTML  += "" // unlimited return
	//		
	//	if (showRank) document.getElementById('currentSettingLabel').innerHTML += "" //" Show rank scores"
	//}else{
	//	document.getElementById('currentSettingLabel').innerHTML  += " Exact matching <br>"	
	//}
	
	if(adsEnable){
		if(Math.random() > 0.4)
			document.getElementById('ads').className += 'hidden'
		else
			document.getElementById('ads').className = '' 
	}
}


// Creates a list of all keywords and attributes specified in the query
function getDisplayAttrs(query) {
	var queryStrs = query.split(',')
	for (i in queryStrs) if (queryStrs[i][0] == '-') return false

	var attrs = []
	var tokens = query.split(' ')
	for (i in tokens) {
		var t = tokens[i]
		if (t.length > 1  && (t.indexOf('(') >= 0 || t.indexOf(')') >= 0)) t = t.match(/\(?\s*(\w+)\s*\)?/)[1]
		// Remove syntax chars
		if (t == '+' || t == '(' || t == ')') {
			if (t.length > 0 && t[1] == 'l') {
				i++
			}
			continue
		} else {
			if ((n=t.search(/[><!=]+/)) > 0) attrs.push(t.substr(0,n))
			else	attrs.push(t)
		}
	}
	return  attrs
}


// Function to create result list from an AJAX response
function objectResp(items, displayElemId, displayAttrs) {
        var l = 0
        var list = document.createElement('ul')
        document.getElementById(displayElemId).innerHTML = ''
        document.getElementById(displayElemId).appendChild(list)
        for (i in items) {
                // Create a list item for every object in the result set
                var listitem = document.createElement('li')
                //if (items.length > 1) listitem.innerHTML =  '<div class="resultNum">' + ++l + '</div>'
				l = l + 1
                listitem.appendChild(objectResult(l, items[i], false, displayAttrs))
                list.appendChild(listitem)
        }
}

// Creates the HTML for each object in the result set
function objectResult(resultNum, object, isHidden, displayAttrs) {
	var score = 0
	if (object instanceof Array) {
		score = object[0]
		object = object[1]
	}
	// use box appearance
	if (useBox) {

		// Creates table of the object to be displayed (limited or full)
		var origTable = createObjectTable(resultNum, object, false, displayAttrs)
	
		// Creates the wrapper for each object result
		var result = document.createElement('div')
		result.id = origTable.id + 'Box'
		result.className = 'box left objectBox'
	
		// Adds a title if object type and name
		var objType = object['object-type']
		if (objType ) {
			var nameAttr = 'object-name'
			if (object[nameAttr]) {
				var name = shorten(object[nameAttr], MAX_NAME_LENGTH, displayAttrs)
				var title = document.createElement('h4')
				title.innerHTML =  name + '<label class="object_type">' + objType + '</label>'
				if (showRank && score) {
					title.innerHTML += '<label class="rank">' + score.toFixed(5) + '</label>'
				}
				title.onclick = function() { switchObjectDisplay(origTable.id) }
				result.appendChild(title)
			}
		}
	
		// Appends the original object result table
		result.appendChild(origTable)
		
		// If only displaying some attrs - go ahead and create a hidden table
		//      with the full object as well
		if (displayAttrs) {
			var fullTable = createObjectTable(resultNum, object , true)
			result.appendChild(fullTable)
			result.appendChild(createObjectLinks('', origTable.id, object))
		} else if(isHidden) {
			result.appendChild(createObjectLinks('full', origTable.id, object))
		}
	} else {
		// Uses new appearance
		// Creates the wrapper for each object result
		var result = document.createElement('div')
		result.id = 'object' + resultNum + 'Box'
		result.className = 'box left objectBox'
		
		// Adds a title if object type and name
		var objType = object['object-type']
		if (objType ) {
			var nameAttr = 'object-name'
			if (object[nameAttr]) {
				var name = shorten(object[nameAttr], MAX_NAME_LENGTH, displayAttrs)
				var title = document.createElement('h4')
				title.innerHTML =  '<label class="object_name">' + name + '</label>'+ '<label class="object_type">' + objType + '</label>'
				if (showRank && score) {
					title.innerHTML += '<label class="rank">' + score.toFixed(5) + '</label>'
				}
				title.onclick = function() { switchObjectDisplay('object'+resultNum) }
				result.appendChild(title)
			}
		}
		// Appends content section
		result.appendChild(createObjectContent(resultNum,object,false))
		result.appendChild(createObjectContent(resultNum,object,true))
		
		// Appends link section
		//result.appendChild(createObjectLinks('', 'object'+resultNum, object))
		
	}
	return result
}

function highLightResult(object, query){
    var highlight = new Object();
    var sub_highlight = new Object();
    var queries = query.split(" ")
    highlight = object
    var cnt =0
    var pre_text = false
    var last_text = false
    for (var i in highlight ){
        cnt++
        for (var j in queries){ 
            var kv = queries[j].split("=")
            if (kv.length == 2){
                search_query = kv[1]
            }else{
                search_query = queries[j]
            }    
            tmp = highlight[i]
            if(isNumber(tmp)){
               tmp = tmp.toString() 
            }    
			if (tmp instanceof Array){
				tmp = tmp.join() 	
			}
            var reg = new RegExp(search_query, 'gi'); 
            high_lighted_text = tmp.replace(reg, function(str) {return '<span class="highlight highlight-on">'+str+'</span>'})
            if (tmp != high_lighted_text){
                if(cnt == 1){
                    pre_text = true 
                }    
                if(cnt == pre_text.length){
                    last_text = true 
                }    
                sub_highlight[i] = high_lighted_text
                highlight[i] = high_lighted_text
            }    
        }    
    }    
    var rtn = new Array(highlight, sub_highlight, pre_text, last_text);
    return rtn
}


function onelineHighLight(result){
    if(isNumber(window.query)){
        query = window.query.toString()
    }
    query = query.trim()
	var tmp = result
        //console.dir(search_query_trim)
		//
	if(isNumber(tmp)){
	   tmp = tmp.toString() 
	}    
	if (tmp instanceof Array){
		tmp = tmp.join(" ") 	
	}
	var matchCandidates = tmp.split(" ")
	var high_lighted_text = ""
	for(var k in matchCandidates){
		if(isNumber(matchCandidates[k])){
		   matchCandidates[k] = matchCandidates[k].toString() 
		}    
		var queries = query.split(" ")
		for (var j in queries){ 
			var kv = queries[j].split("=")
			if (kv.length == 2){
				search_query = kv[1]
			}else{
				search_query = queries[j]
			}    
			if(isNumber(search_query)){
				search_query = search_query.toString()
			}
			search_query_trim = search_query.trim()
			var reg = new RegExp(search_query, 'gi'); 
			matchCandidates[k] = matchCandidates[k].replace(reg, function(str) {return '<span class="highlight highlight-on">'+str+'</span>'}) + " "

        }
		high_lighted_text += matchCandidates[k]

	}
	return high_lighted_text
}

// create content of an object 
function createObjectContent(id,object,isFull){
	var content = document.createElement('div')
	content.id = 'object'+id
	content.className = 'content left detail-of-content'

	var objType = object['object-type']
	var contentText = ''
	var SEP = ' '

	// Create a table using all attrs and vals , then hide it
	if (isFull) {  
		content.id += 'Full'
		content.className = 'hidden detail-of-content'
		// create a content infomation based on predefine format
		if(isProject){
			for (var i in object){
				if (i !='object-name' && i != 'object-type')
					var key = onelineHighLight(i)
					var val = onelineHighLight(object[i])
					contentText += key+': <span style="font-weight:normal;">' + val + '</span><br> ' 
			}
		}else{
			for (var i in object){
				var key = onelineHighLight(i)
				var val = onelineHighLight(object[i])
				if (typeof object[i] == 'number')
					contentText += key+': <span style="font-weight:normal;">' + val + '</span><br> ' 
				else if (i =='object-url')
					contentText += key+': <a href= "'+ object[i] +'" target="_blank">' + val + '</a><br> ' 
				else if(i == 'raw-output')
					contentText += key+': <br /><pre>' + val + '</pre><br /> ' 
				else
					contentText += key+': <span style="font-weight:normal;">' + val + '</span><br> '
			}
		}
	}else{
		for (var i in object){
			contentText +=  i + ' ' + object[i] + ' ' 
		}
		contentText = shorten(contentText,200) 
		contentText = onelineHighLight(contentText)
	}
	content.innerHTML = contentText
	return content

}

// Create a new string from a long string given a length, a set of attrs to highlight
function shorten(str, maxLen, displayAttrs) {
	var minLen = maxLen / 2	

	// Return if this string is already short
	if (str.length <= maxLen) return str

	// Then find any displayAttrs in the 2nd half of string and record their location
	var attrs = []
	for (i in displayAttrs) {
		var attr = displayAttrs[i]
		var idx = str.indexOf(attr, minLen -1)
		if (idx > -1) {
			attrs[idx] = attr
		}
	}

	// Create a new string with ellipses
	var attrStr = ''
	var lastIndex = minLen
	for (var i in attrs) {
		var attr = attrs[i]
		if (attr && attrStr.indexOf(attr) < 0) {
			if (parseInt(i) > lastIndex + 1) attrStr += '...'
			attrStr += attr
			lastIndex = parseInt(i)
		}
	}
	// Shorten the string, and add ellipses if needed
	var newLen = maxLen - attrStr.length
	if (str.length > newLen) {
		str = str.substr(0, maxLen - attrStr.length)
		str += attrStr
		str += '...'
	}
	return str
}

function isNumber(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}


function noenter() {
  if (window.event.keyCode == 13){
	search()
	return false
  } 
}


$("#max_result").blur(function(){ 
	addSettingsCookie('max_result', $(this).val())
 });

// Get searches from cookie
function getCookie(name)
{
    var queries
    var cs = document.cookie.split("; ")
    for (c=0; c<cs.length; c++) {
        var attrval = cs[c].split("=")
        if (attrval[0] == name) {
            queries = unescape(attrval[1]).split("&")
            break
        }    
    }    
    return queries
}

function addSettingsCookie(name , value) {
        var exdate = new Date()
        exdate.setDate(exdate.getDate() + COOKIE_EXP)

        var c = name +"=" + value + "; expires=" + exdate.toUTCString()
        document.cookie = c
        console.dir(c)
        //document.location = '/'
}

// Function to switch the limited display of an object with the full display
function switchObjectDisplay(id, showFull) {
    if (id) {
        if (showFull == null) showFull = document.getElementById(id).className != 'hidden'        
        var link = document.getElementById(id + 'SwitchLink')
        if (showFull) {
            showElem = document.getElementById(id + 'Full')
            hideElem = document.getElementById(id)
            if (link) link.innerHTML = 'Show less'
        } else {
            showElem = document.getElementById(id)
            hideElem = document.getElementById(id + 'Full')
            if (link) link.innerHTML = 'See more Information'
        }    

        if (hideElem) hideElem.className = 'hidden'
        if (showElem) showElem.className = 'content left'
    }    
}

// High Light function
$('#highlight-switch').on('click', function(e){
    $(this).toggleClass("btn-warning btn-default");
    $('#highlight-btn-text').toggleClass("black");
    $('.highlight').toggleClass("highlight-on");
});

$('#expand-switch').on('click',function(e){
    $(this).toggleClass("btn-success btn-default");
    $('#expand-btn-text').toggleClass("black");
    $('.detail-of-content').toggleClass("hidden");
});

