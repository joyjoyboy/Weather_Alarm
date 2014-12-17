package wenxiao.com.weatherapp;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.location.Address;
import android.location.Criteria;
import android.location.Geocoder;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.provider.Settings;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;
import com.loopj.android.http.RequestParams;

import org.apache.http.Header;

import java.io.IOException;
import java.util.List;
import java.util.Locale;


public class Login extends Activity {

    private EditText userName;
    private EditText password;
    private AsyncHttpClient httpClient = new AsyncHttpClient();
    private static final String Request_URL = "http://electric-facet-794.appspot.com/androidVerificationHandler";
    private LocationManager locationManager;
    private String provider;
    private Criteria criteria;
    private String currentAddress;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        // ********** Retrieve current location **********
        // Set up the location manager
        locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
        // Define the criteria how to select the location provider
        // Use network locating service by default
        criteria = new Criteria();
        criteria.setAccuracy(Criteria.ACCURACY_COARSE);
        criteria.setCostAllowed(false);
        // get the best provider depending on the criteria
        provider = locationManager.getBestProvider(criteria, false);

        // the last known location of this provider
        Location location = locationManager.getLastKnownLocation(provider);
        Geocoder geocoder = new Geocoder(getApplicationContext(), Locale.getDefault());
        try {
            List<Address> listAddresses = geocoder.getFromLocation(location.getLatitude(), location.getLongitude(), 1);
            if(null != listAddresses && listAddresses.size() > 0){
                currentAddress = listAddresses.get(0).getAddressLine(1);
            }
            else{
                currentAddress = "";
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        // ********** End of retrieving location *********

        userName = (EditText) findViewById(R.id.userName);
        password = (EditText) findViewById(R.id.password);

        Button buttonSignIn = (Button) findViewById(R.id.signIn);
        Button buttonSignUp = (Button) findViewById(R.id.signUp);

        buttonSignIn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String userNameContent = userName.getText().toString();
                String passwordContent = password.getText().toString();

                if((userNameContent != null && !userNameContent.isEmpty()) && (passwordContent != null && !passwordContent.isEmpty()) && !currentAddress.isEmpty()) {

                    RequestParams params = new RequestParams();
                    params.put("userName", userNameContent);
                    params.put("password", passwordContent);
                    params.put("Type", "signIn");
                    params.put("Addr", currentAddress);

                    httpClient.post(Request_URL, params, new AsyncHttpResponseHandler() {
                        @Override
                        public void onSuccess(int statusCode, Header[] headers, byte[] response) {
                            String result = new String(response);
                            if(result.equals("YES")) {
                                //Toast.makeText(Login.this, "Successful log in", Toast.LENGTH_SHORT).show();
                                String userNameStr = userName.getText().toString();
                                Intent MainPage = new Intent(Login.this, ConsoleActivity.class);
                                MainPage.putExtra("userName", userNameStr);
                                MainPage.putExtra("currAddr", currentAddress);
                                Login.this.startActivity(MainPage);
                            }
                            else{
                                Toast.makeText(Login.this, "Incorrect username or password", Toast.LENGTH_SHORT).show();
                            }
                        }

                        @Override
                        public void onFailure(int statusCode, Header[] headers, byte[] errorResponse, Throwable e) {
                            Log.e("Sign in verification ", "Failed!");
                            Toast.makeText(Login.this, "Connection failed", Toast.LENGTH_SHORT).show();
                        }
                    });

                }
                else{
                    Toast.makeText(Login.this, "Please enter username and password", Toast.LENGTH_SHORT).show();
                }
            }
        });

        buttonSignUp.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String userNameContent = userName.getText().toString();
                String passwordContent = password.getText().toString();

                if((userNameContent != null && !userNameContent.isEmpty()) && (passwordContent != null && !passwordContent.isEmpty()) && !currentAddress.isEmpty()) {

                    RequestParams params = new RequestParams();
                    params.put("userName", userNameContent);
                    params.put("password", passwordContent);
                    params.put("Type", "signUp");
                    params.put("Addr", currentAddress);

                    httpClient.post(Request_URL, params, new AsyncHttpResponseHandler() {
                        @Override
                        public void onSuccess(int statusCode, Header[] headers, byte[] response) {
                            String result = new String(response);
                            if(result.equals("YES")){
                                //Toast.makeText(Login.this, "Successful sign up", Toast.LENGTH_SHORT).show();
                                String userNameStr = userName.getText().toString();
                                Intent MainPage = new Intent(Login.this, ConsoleActivity.class);
                                MainPage.putExtra("userName", userNameStr);
                                MainPage.putExtra("currAddr", currentAddress);
                                Login.this.startActivity(MainPage);
                            }
                            else{
                                Toast.makeText(Login.this, "This username has been used", Toast.LENGTH_SHORT).show();
                            }
                        }

                        @Override
                        public void onFailure(int statusCode, Header[] headers, byte[] errorResponse, Throwable e) {
                            Toast.makeText(Login.this, "Connection failed", Toast.LENGTH_SHORT).show();
                        }
                    });

                }
                else{
                    Toast.makeText(Login.this, "Please enter username and password", Toast.LENGTH_SHORT).show();
                }
            }
        });

    }
}
