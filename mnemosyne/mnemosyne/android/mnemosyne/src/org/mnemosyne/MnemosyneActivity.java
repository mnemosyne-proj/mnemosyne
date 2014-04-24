package org.mnemosyne;

import java.io.IOException;
import java.io.InputStream;

import android.app.Activity;
import android.content.res.AssetManager;
import android.os.Bundle;
import android.widget.TextView;

import com.srplab.www.starcore.*;

public class MnemosyneActivity extends Activity {

	static TextView MyEdit1;
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        
        MyEdit1 = (TextView)this.findViewById(R.id.widget61);
        
        try {
        	AssetManager assetManager = getAssets();
        	InputStream dataSource = assetManager.open("testpy.zip");
        	StarCoreFactoryPath.CreatePath(Runtime.getRuntime(),"/data/data/"+getPackageName()+"/files");
        	StarCoreFactoryPath.Install(dataSource, "/data/data/"+getPackageName()+"/files",true );
        }
        catch (IOException e) {
        }        	        	
        
        StarCoreFactoryPath.StarCoreCoreLibraryPath = "/data/data/"+ getPackageName()+"/lib";
        StarCoreFactoryPath.StarCoreShareLibraryPath = "/data/data/"+getPackageName()+"/lib";
        StarCoreFactoryPath.StarCoreOperationPath = "/data/data/"+getPackageName()+"/files";
        StarCoreFactory starcore = StarCoreFactory.GetFactory();
        
        StarSrvGroupClass SrvGroup = starcore._GetSrvGroup(0); 
        StarServiceClass Service = SrvGroup._GetService("test", "123");
        if ( Service == null ) {  // The service has not been initialized.
          Service = starcore._InitSimple("test", "123", 0, 0);
          Service._CheckPassword(false);
          SrvGroup = (StarSrvGroupClass) Service._Get("_ServiceGroup");

          SrvGroup._InitRaw("python", Service);
          SrvGroup._LoadRawModule("python", "", "/data/data/" + getPackageName() + "/files/testpy.py", false);
          //SrvGroup._LoadRawModule("python", "", "/data/data/" + getPackageName() + "/files/callback.py", false);
          //Service._DoFile("python", "/data/data/"+getPackageName()+"/files/callback.py", "");
        }
		
		//--Attach object to global Python space
		StarObjectClass python = Service._ImportRawContext("python", "", false, "");  
		//--all Python function tt, the return contains two integer, which will be packed into parapkg
		StarParaPkgClass ParaPkg = (StarParaPkgClass)python._Call("tt","hello ","world");
		printStr("ret from python :  "+ParaPkg._Get(0)+"   "+ParaPkg._Get(1));
		//--get global int value g1
		printStr("python value g1 :  "+python._Get("g1"));

		//--call Python function yy, the return is dict, which will be mapped to cle object
		StarObjectClass yy = (StarObjectClass) python._Call("yy","hello ","world",123);
		//--call dict __len__ function to get dict length
		printStr("python value dict length :  "+yy._Call("__len__"));

		//--get global class Multiply
		StarObjectClass Multiply = Service._ImportRawContext("python", "Multiply", true, null);
		StarObjectClass multiply = Multiply._Callobject("_StarCall",33,44);
		//--call instance method multiply
		printStr("instance multiply = " + multiply._Call("multiply",11,22));
		
		
        //--attach object to testpy.Class1 ---*/
        //StarObjectClass TestCallBack = Service._ImportRawContext("python", "Class1", true, ""); 
        //--create an instance of TestCallBack-----*/
        //StarObjectClass inst = TestCallBack._Callobject("_StarCall");
	
		StarObjectClass inst = (StarObjectClass) python._Get("class1");
        
        // Create object and functions for proxy----*/
		
        StarObjectClass object = Service._New()._Assign(new StarObjectClass() {
        	
        	public void postExec(StarObjectClass self) {
        		printStr("Callback in Java from Python.");
            };
                    
             public float getNum(StarObjectClass self, StarParaPkgClass input) {
               	printStr("Callback [getNum] in Java from Python : " + input._Get(0) + "    " + input._Get(1));
                return (float)(input._Getdouble(0) + input._Getdouble(1));
             };
             
        });
       
        // Create proxy for interface testcallback/ICallBack ---*/
        StarObjectClass proxy1 = Service._NewRawProxy("python", object, "postExec", "_name_does_not_seem_to_matter_Class1.postExec", 0);
        StarObjectClass proxy2 = Service._NewRawProxy("python", object, "getNum", "Class1.getNum", 0);
        //--set the proxy to TestCallBack instance ---*/
        inst._Call("setCallBack", proxy1, proxy2);
        //--now proxy can be freed----*/
        proxy1._Free();
        proxy2._Free();

        //--call inst function postExec----*/
        inst._Call("postExec");
        //--call inst function getNum----*/
        printStr(inst._Call("getNum", SrvGroup._NewParaPkg(123.0,456.0)));    
    }
    
    private void printStr(Object str)
    {
    	String in_Str;
    	
    	in_Str = MyEdit1.getText().toString();
    	in_Str = in_Str + "\n" + str;
    	MyEdit1.setText(in_Str);    	
    }
}