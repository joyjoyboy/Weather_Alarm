package wenxiao.com.weatherapp;

import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.widget.Toast;


public class Alarm extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent)
    {
        context.stopService(new Intent(context, NotificationService.class));
        String currentUser = intent.getStringExtra("userName");
        Intent serviceIntent = new Intent(context, NotificationService.class);
        serviceIntent.putExtra("userName", currentUser);
        context.startService(serviceIntent);
    }

}
