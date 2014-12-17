package wenxiao.com.weatherapp;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;
import com.loopj.android.http.RequestParams;

import org.apache.http.Header;


public class CalendarHandler extends Activity {

    private AsyncHttpClient httpClient = new AsyncHttpClient();
    private static final String Request_URL = "http://electric-facet-794.appspot.com/calendarHandler";
    private String currentUser;
    private String currAddr;

    EditText city;
    EditText state;
    EditText targetDate;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_calendarhandler);

        Intent intent = getIntent();
        currentUser = intent.getStringExtra("userName");
        currAddr = intent.getStringExtra("Addr");

        city = (EditText) findViewById(R.id.city);
        state = (EditText) findViewById(R.id.state);
        targetDate = (EditText) findViewById(R.id.date);

        Button buttonBack = (Button) findViewById(R.id.back);
        Button buttonSubmit = (Button) findViewById(R.id.submit);

        buttonBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent ConsolePage = new Intent(CalendarHandler.this, ConsoleActivity.class);
                ConsolePage.putExtra("userName", currentUser);
                ConsolePage.putExtra("Addr", currAddr);
                CalendarHandler.this.startActivity(ConsolePage);
            }
        });

        buttonSubmit.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                RequestParams params = new RequestParams();
                params.put("userName", currentUser);
                params.put("Addr", city.getText().toString() + " " + state.getText().toString());
                params.put("Date", targetDate.getText().toString());

                httpClient.post(Request_URL, params, new AsyncHttpResponseHandler() {
                    @Override
                    public void onSuccess(int statusCode, Header[] headers, byte[] response) {
                        String result = new String(response);
                        if(result.equals("YES")) {
                            Toast.makeText(CalendarHandler.this, "Added to calendar", Toast.LENGTH_SHORT).show();
                            Intent ConsolePage = new Intent(CalendarHandler.this, ConsoleActivity.class);
                            ConsolePage.putExtra("userName", currentUser);
                            ConsolePage.putExtra("Addr", currAddr);
                            CalendarHandler.this.startActivity(ConsolePage);
                        }
                        else{
                            Toast.makeText(CalendarHandler.this, "Failed to add to calendar", Toast.LENGTH_SHORT).show();
                        }
                    }

                    @Override
                    public void onFailure(int statusCode, Header[] headers, byte[] errorResponse, Throwable e) {
                        Toast.makeText(CalendarHandler.this, "Failed location update", Toast.LENGTH_SHORT).show();
                    }
                });

            }
        });
    }
}
