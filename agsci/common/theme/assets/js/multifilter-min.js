var multiFilter={$filterGroups:null,$filterUi:null,$reset:null,groups:[],outputArray:[],outputString:"",init:function(){var t=this;t.$filterUi=$("#Filters"),t.$filterGroups=$(".filter-group"),t.$reset=$("#Reset"),t.$container=$("#Container"),t.$filterGroups.each(function(){t.groups.push({$inputs:$(this).find("input"),active:[],tracker:!1})}),t.bindHandlers()},bindHandlers:function(){var t=this,e=300,r=-1,i=function(){clearTimeout(r),r=setTimeout(function(){t.parseFilters()},300)};t.$filterGroups.filter(".checkboxes").on("change",function(){t.parseFilters()}),t.$filterGroups.filter(".search").on("keyup change",i),t.$reset.on("click",function(e){e.preventDefault(),t.$filterUi[0].reset(),t.$filterUi.find('input[type="text"]').val(""),t.parseFilters()})},parseFilters:function(){for(var t=this,e=0,r;r=t.groups[e];e++)r.active=[],r.$inputs.each(function(){var t="",e=$(this),i=3;e.is(":checked")&&r.active.push(this.value),e.is('[type="text"]')&&this.value.length>=3&&(t=this.value.trim().toLowerCase().replace(" ","-"),r.active[0]='[class*="'+t+'"]')}),r.active.length&&(r.tracker=0);t.concatenate()},concatenate:function(){var t=this,e="",r=!1,i=function(){for(var e=0,r=0,i;i=t.groups[r];r++)!1===i.tracker&&e++;return e<t.groups.length},n=function(){for(var r=0,i;i=t.groups[r];r++)i.active[i.tracker]&&(e+=i.active[i.tracker]),r===t.groups.length-1&&(t.outputArray.push(e),e="",u())},u=function(){for(var e=t.groups.length-1;e>-1;e--){var i=t.groups[e];if(i.active[i.tracker+1]){i.tracker++;break}e>0?i.tracker&&(i.tracker=0):r=!0}};t.outputArray=[];do{n()}while(!r&&i());t.outputString=t.outputArray.join(),!t.outputString.length&&(t.outputString="all"),console.log(t.outputString),t.$container.mixItUp("isLoaded")&&t.$container.mixItUp("filter",t.outputString)}};$(function(){multiFilter.init(),$("#Container").mixItUp({controls:{enable:!1},animation:{easing:"cubic-bezier(0.86, 0, 0.07, 1)",queueLimit:3,duration:600}})});