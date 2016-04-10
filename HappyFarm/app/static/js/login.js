window.onload=function(){
    var oLog_in = document.getElementsById("log_in");
    var oUl = oLog_in.getElementsByTagName("ul")[0];
    var oLis = oUl.getElementsByTagName("li");
    var oDivs = oLog_in.getElementsByTagName("div");
    for(var i=0,len = oLis.length;i<len;i++){
      oLis[i].index = i;
      oLis[i].onclick = function(){
        for(var n=0;n<len;n++)
        {
          oLis[n].className = "";
          oDivs[n].className="hide";
        }
        this.className = "on";
        oDivs[this.index].className="";
      }
    };
}
