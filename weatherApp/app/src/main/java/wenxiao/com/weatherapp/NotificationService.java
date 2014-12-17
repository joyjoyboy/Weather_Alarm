package wenxiao.com.weatherapp;

import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.media.Ringtone;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.IBinder;
import android.support.v4.app.NotificationCompat;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Toast;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;
import com.loopj.android.http.RequestParams;

import org.apache.http.Header;

import java.util.Calendar;


public class NotificationService extends Service {

    private AsyncHttpClient httpClient = new AsyncHttpClient();
    private static final String Request_URL = "http://electric-facet-794.appspot.com/pollingHandler";
    NotificationCompat.Builder mBuilder =
            new NotificationCompat.Builder(this);


    private String currentUser;

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        currentUser = intent.getStringExtra("userName");
        final Intent resultIntent = new Intent(this, ConsoleActivity.class);
        final PendingIntent resultPendingIntent =
                PendingIntent.getActivity(
                        this,
                        0,
                        resultIntent,
                        PendingIntent.FLAG_UPDATE_CURRENT
                );

        RequestParams params = new RequestParams();
        params.put("userName", currentUser);

        httpClient.post(Request_URL, params, new AsyncHttpResponseHandler() {
            @Override
            public void onSuccess(int statusCode, Header[] headers, byte[] response) {
                String result = new String(response);
                if(!result.isEmpty()) {

                    mBuilder.setSmallIcon(R.drawable.ic_launcher)
                            .setContentTitle("Weather Alert")
                            .setContentText(result)
                            .setContentIntent(resultPendingIntent);
                    int mNotificationId = 1;
                    NotificationManager mNotifyMgr =
                            (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
                    mNotifyMgr.notify(mNotificationId, mBuilder.build());
                    Toast.makeText(NotificationService.this, "Weather Change Alert", Toast.LENGTH_SHORT).show();
                    try {
                        Uri notification = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
                        Ringtone r = RingtoneManager.getRingtone(getApplicationContext(), notification);
                        r.play();
                    } catch (Exception e) {
                        e.printStackTrace();
                    }

                }
                else{
                    // No result for this user
                }
            }

            @Override
            public void onFailure(int statusCode, Header[] headers, byte[] errorResponse, Throwable e) {
                Toast.makeText(NotificationService.this, "Polling request failed", Toast.LENGTH_SHORT).show();
            }
        });

        return START_STICKY;
    }

    public void onCreate()
    {
        super.onCreate();
    }

    @Override
    public IBinder onBind(Intent intent)
    {
        return null;
    }


}
