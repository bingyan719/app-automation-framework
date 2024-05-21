function getUrlParam(name) {
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
        var r = window.location.search.substr(1).match(reg);  //匹配目标参数
        if (r != null) return unescape(r[2]); return null; //返回参数值
}
String.prototype.trim=function() {  
    return this.replace(/(^\s*)|(\s*$)/g,'');  
}; 
/*
$(function () {
    $.getJSON(
	"report/jsonReport.json", 
	function(json){
  alert(json);
});

   // $('#dg').datagrid("loadData", getData());//datagrid({ loadFilter: pagerFilter });
});
*/ 
function DataCtrl($scope) {
/*
  switch(testSuits.driverType)
  {

    case 'UIAutomator':
    case 'Selendroid':
    case 'UIAutomation':
      testSuits.appInfo.packageURI=testSuits.appInfo.packageURI.substr(testSuits.appInfo.packageURI.lastIndexOf('\\')+1);
    break;
    case 'ChromeDriver':
    case 'IOSWebkit':
    default:
    break;
  }
*/  
  $scope.testSuits = testSuits;
  $scope.testSuits['_startTime']=testSuits._startTime;
  $scope.testSuits['passrate']=testSuits['_total']==0?'':(100*(testSuits['_success'])/(testSuits['_total'])).toFixed(2)+"%";
  $.each($scope.testSuits['_suites'],function (i,suite) {
    suite['id']=md5(JSON.stringify(suite));
    suite['passrate']=suite['_total']==0?'':(100*(suite['_success'])/(suite['_total'])).toFixed(2)+"%";
	suite['suiteName']=suite._suite_name;

    $.each(suite['_test_classes_list'],function(j,testclass)
      {
        testclass['id']=md5(JSON.stringify(testclass));
        $.each(testclass['_case_list'],function(j,singleclass)
          {
            singleclass['id']=md5(JSON.stringify(singleclass));
          });

      });

  });
}