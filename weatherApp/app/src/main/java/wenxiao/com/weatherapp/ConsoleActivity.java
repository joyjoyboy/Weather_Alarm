package wenxiao.com.weatherapp;

import android.app.Activity;
import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.location.Address;
import android.location.Criteria;
import android.location.Geocoder;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.provider.Settings;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.TextView;
import android.widget.Toast;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;
import com.loopj.android.http.RequestParams;

import org.apache.http.Header;

import java.io.IOException;
import java.util.List;
import java.util.Locale;

import static java.security.AccessController.getContext;

public class ConsoleActivity extends Activity {

    private AsyncHttpClient httpClient = new AsyncHttpClient();
    private AsyncHttpClient httpClientForCurrentWeather = new AsyncHttpClient();
    private static final String Request_URL = "http://electric-facet-794.appspot.com/androidRequestHandler";
    private static final String Weather_Request_URL = "http://electric-facet-794.appspot.com/androidWeatherRequestHandler";
    private String currentAddress;
    private String currentUser;
    private TextView latitude;
    private TextView longitude;
    private TextView addr;
    private TextView currTemperature;
    private LocationManager locationManager;
    private String provider;
    private MyLocationListener mylistener;
    private Criteria criteria;
    private PendingIntent pendingIntent;

    /** Called when the activity is first created. */

    @Override
    public void onCreate(Bundle savedInstanceState) {

        // Render mobile UI
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_console);

        Intent getCurrIntent = getIntent();
        currentUser = getCurrIntent.getStringExtra("userName");
        currentAddress = getCurrIntent.getStringExtra("currAddr");

        Button buttonAddCalendar = (Button) findViewById(R.id.addCalendar);
        buttonAddCalendar.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent CalendarPage = new Intent(ConsoleActivity.this, CalendarHandler.class);
                CalendarPage.putExtra("userName", currentUser);
                ConsoleActivity.this.startActivity(CalendarPage);
            }
        });

        latitude = (TextView) findViewById(R.id.lat);
        longitude = (TextView) findViewById(R.id.lon);
        addr = (TextView) findViewById(R.id.addr);
        currTemperature = (TextView) findViewById(R.id.currTemperature);

        addr.setText(currentAddress);

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

        mylistener = new MyLocationListener();

        if (location != null) {
            mylistener.onLocationChanged(location);
        } else {
            // leads to the settings because there is no last known location
            Intent intent = new Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS);
            startActivity(intent);
        }
        // location updates
        // at least 1 kilometer and 10 minute (600 seconds) change
        locationManager.requestLocationUpdates(provider, 600000, 1000, mylistener);

        // Background polling service
        Intent alarmIntent = new Intent(ConsoleActivity.this, Alarm.class);
        alarmIntent.putExtra("userName", currentUser);
        pendingIntent = PendingIntent.getBroadcast(ConsoleActivity.this, 0, alarmIntent, 0);

        AlarmManager manager = (AlarmManager) getSystemService(Context.ALARM_SERVICE);
        // 5 mins per polling request
        int interval = 30000;

        manager.setInexactRepeating(AlarmManager.RTC_WAKEUP, System.currentTimeMillis(), interval, pendingIntent);
    }

    @Override
    public void onResume(){
        super.onResume();

        addr.setText(currentAddress);
        RequestParams params = new RequestParams();
        params.put("userName", currentUser);
        params.put("addr", currentAddress);

        httpClientForCurrentWeather.post(Weather_Request_URL, params, new AsyncHttpResponseHandler() {
            @Override
            public void onSuccess(int statusCode, Header[] headers, byte[] response) {
                String result = new String(response);
                currTemperature.setText("Temperature: " + result);
            }

            @Override
            public void onFailure(int statusCode, Header[] headers, byte[] errorResponse, Throwable e) {
                Toast.makeText(ConsoleActivity.this, "Failed temperature update", Toast.LENGTH_SHORT).show();
            }
        });

    }

    private class MyLocationListener implements LocationListener {

        @Override
        public void onLocationChanged(Location location) {
            // Initialize the location fields
            latitude.setText("Latitude: " + String.valueOf(location.getLatitude()));
            longitude.setText("Longitude: " + String.valueOf(location.getLongitude()));

            addr.setText(currentAddress);
            Toast.makeText(ConsoleActivity.this, "Location changed!", Toast.LENGTH_SHORT).show();

            Geocoder geocoder = new Geocoder(getApplicationContext(), Locale.getDefault());
            try {
                List<Address> listAddresses = geocoder.getFromLocation(location.getLatitude(), location.getLongitude(), 1);
                if(null != listAddresses && listAddresses.size() > 0){
                    String currLocation = listAddresses.get(0).getAddressLine(1);
                    // Address has been updated
                    if(!currLocation.equals(currentAddress)){

                        currentAddress = currLocation;
                        RequestParams params = new RequestParams();
                        params.put("userName", currentUser);
                        params.put("addr", currentAddress);

                        httpClient.post(Request_URL, params, new AsyncHttpResponseHandler() {
                            @Override
                            public void onSuccess(int statusCode, Header[] headers, byte[] response) {
                                String result = new String(response);
                                if(result.equals("YES")) {
                                    Toast.makeText(ConsoleActivity.this, "Successful location update", Toast.LENGTH_SHORT).show();
                                }
                                else{
                                    Toast.makeText(ConsoleActivity.this, "Failed location update", Toast.LENGTH_SHORT).show();
                                }
                            }

                            @Override
                            public void onFailure(int statusCode, Header[] headers, byte[] errorResponse, Throwable e) {
                                Toast.makeText(ConsoleActivity.this, "Failed location update", Toast.LENGTH_SHORT).show();
                            }
                        });

                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
            }

        }

        @Override
        public void onStatusChanged(String provider, int status, Bundle extras) {
            Toast.makeText(ConsoleActivity.this, provider + "'s status changed to "+status +"!", Toast.LENGTH_SHORT).show();
        }

        @Override
        public void onProviderEnabled(String provider) {
            Toast.makeText(ConsoleActivity.this, "Provider " + provider + " enabled!", Toast.LENGTH_SHORT).show();
        }

        @Override
        public void onProviderDisabled(String provider) {
            Toast.makeText(ConsoleActivity.this, "Provider " + provider + " disabled!", Toast.LENGTH_SHORT).show();
        }
    }

}