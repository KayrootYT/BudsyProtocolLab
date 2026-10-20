from pathlib import Path

source = Path("BudsyProtocolLab/app/src/main/java/com/budsy/protocollab/MainActivity.java")
s = source.read_text(encoding="utf-8")
if "scanResults = new LinkedHashMap" in s:
    print("BLE discovery patch already applied")
    raise SystemExit(0)
s = s.replace("import android.bluetooth.le.ScanResult;", "import android.bluetooth.le.ScanResult;\nimport android.bluetooth.le.ScanSettings;")
s = s.replace("import java.util.HashMap;", "import java.util.HashMap;\nimport java.util.LinkedHashMap;\nimport java.util.Collections;")
s = s.replace("    private final Map<String, BluetoothDevice> found = new HashMap<>();", "    private final Map<String, BluetoothDevice> found = new LinkedHashMap<>();\n    private final Map<String, ScanResult> scanResults = new LinkedHashMap<>();\n    private final Map<String, BluetoothDevice> bondedDevices = new LinkedHashMap<>();\n    private final Runnable stopScanTask = this::stopScan;\n    private boolean pendingScan = false;")
start = s.index("    private void requestBtPermissions() {")
end = s.index("    private final BluetoothGattCallback gattCallback", start)
replacement = '''    private boolean hasBtPermissions() {
        if (Build.VERSION.SDK_INT >= 31) return checkSelfPermission(Manifest.permission.BLUETOOTH_SCAN)==PackageManager.PERMISSION_GRANTED && checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT)==PackageManager.PERMISSION_GRANTED;
        return Build.VERSION.SDK_INT < 23 || checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)==PackageManager.PERMISSION_GRANTED;
    }
    private void requestBtPermissions() {
        if (Build.VERSION.SDK_INT >= 31) {
            ArrayList<String> p = new ArrayList<>();
            if (checkSelfPermission(Manifest.permission.BLUETOOTH_SCAN)!=PackageManager.PERMISSION_GRANTED) p.add(Manifest.permission.BLUETOOTH_SCAN);
            if (checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT)!=PackageManager.PERMISSION_GRANTED) p.add(Manifest.permission.BLUETOOTH_CONNECT);
            if (!p.isEmpty()) requestPermissions(p.toArray(new String[0]), 8);
        } else if (Build.VERSION.SDK_INT >= 23 && checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)!=PackageManager.PERMISSION_GRANTED) requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION},8);
    }
    @Override public void onRequestPermissionsResult(int requestCode,String[] permissions,int[] results) {
        super.onRequestPermissionsResult(requestCode,permissions,results);
        if(requestCode==8){
            boolean ok=hasBtPermissions();
            if(!ok){ pendingScan=false; toast("Bluetooth permission denied. Allow Nearby devices (and Location on Android 11 or older)."); }
            else if(pendingScan){ pendingScan=false; startScan(); }
        }
    }
    private void startScan() {
        if (adapter == null) { toast("This phone has no Bluetooth adapter."); return; }
        if (!hasBtPermissions()) { pendingScan=true; requestBtPermissions(); return; }
        if (!adapter.isEnabled()) { toast("Turn Bluetooth on first."); return; }
        try {
            handler.removeCallbacks(stopScanTask);
            scanner=adapter.getBluetoothLeScanner();
            if(scanner==null){toast("BLE scanner unavailable. Check Bluetooth is enabled.");return;}
            if(scanning) { try { scanner.stopScan(scanCallback); } catch(Exception ignored) {} }
            found.clear(); scanResults.clear(); bondedDevices.clear();
            try { for(BluetoothDevice paired:adapter.getBondedDevices()) bondedDevices.put(paired.getAddress(),paired); } catch(SecurityException ignored) {}
            deviceList.removeAllViews();
            deviceList.addView(text("Scanning… paired devices and all BLE advertisements are shown.",12,muted));
            renderDevices();
            ScanSettings settings = new ScanSettings.Builder().setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY).setCallbackType(ScanSettings.CALLBACK_TYPE_ALL_MATCHES).build();
            scanner.startScan(null,settings,scanCallback);
            scanning=true; status.setText("Scanning nearby BLE devices… keep the buds case open");
            addLog("SCAN_START", "", "", "low-latency, all BLE devices");
            handler.postDelayed(stopScanTask,15000);
        } catch(Exception e){ scanning=false; addLog("SCAN_ERROR","","",e.toString()); toast("Scan failed: "+e.getMessage()); }
    }
    private String advertisedName(ScanResult result) {
        String name = null;
        try { if(result.getScanRecord()!=null) name=result.getScanRecord().getDeviceName(); } catch(Exception ignored) {}
        if(name==null || name.trim().isEmpty()) try { name=result.getDevice().getName(); } catch(SecurityException ignored) {}
        return name==null ? "" : name.trim();
    }
    private boolean looksLikeOnePlusBuds(String name) {
        String n=name.toLowerCase(Locale.ROOT).replace("-"," ").replace("_"," ");
        return n.contains("oneplus") || n.contains("one plus") || n.contains("nord buds") || n.contains("buds 3") || n.contains("buds3");
    }
    private void renderDevices() {
        deviceList.removeAllViews();
        if(scanResults.isEmpty() && bondedDevices.isEmpty()) { deviceList.addView(text("No BLE advertisements received yet. Keep the buds case open, wake the earbuds, and scan again. If connected to another phone/app, disconnect it first.",12,muted)); return; }
        ArrayList<ScanResult> results = new ArrayList<>(scanResults.values());
        Collections.sort(results, (a,b) -> Integer.compare(b.getRssi(),a.getRssi()));
        for(ScanResult result:results) {
            BluetoothDevice d=result.getDevice(); String key=d.getAddress(); String name=advertisedName(result);
            String shown=name.isEmpty()?"Unnamed BLE device":name;
            boolean candidate=looksLikeOnePlusBuds(name);
            LinearLayout card=card();
            LinearLayout info=new LinearLayout(this); info.setOrientation(LinearLayout.VERTICAL);
            TextView nameView=text(shown,15,white); nameView.setTypeface(null,1); info.addView(nameView);
            info.addView(text((candidate?"Possible OnePlus earbuds · ":"")+key+" · RSSI "+result.getRssi()+" dBm",12,candidate?orange:muted));
            if(name.isEmpty()) info.addView(text("Name hidden in advertisement; you can still try Connect.",11,muted));
            card.addView(info);
            Button connect=button("Connect GATT"); connect.setOnClickListener(v->connect(d,shown)); card.addView(connect);
            deviceList.addView(card);
        }
        for(BluetoothDevice d:bondedDevices.values()) {
            String key=d.getAddress(); if(scanResults.containsKey(key)) continue;
            String deviceName="Paired Bluetooth device"; try { if(d.getName()!=null && !d.getName().trim().isEmpty()) deviceName=d.getName().trim(); } catch(SecurityException ignored) {}
            final String name=deviceName; boolean candidate=looksLikeOnePlusBuds(name);
            LinearLayout card=card(); LinearLayout info=new LinearLayout(this); info.setOrientation(LinearLayout.VERTICAL);
            TextView nameView=text(name,15,white); nameView.setTypeface(null,1); info.addView(nameView);
            info.addView(text((candidate?"Possible OnePlus earbuds · ":"")+"Paired · not currently advertising · "+key,12,candidate?orange:muted));
            card.addView(info); Button connect=button("Connect GATT"); connect.setOnClickListener(v->connect(d,name)); card.addView(connect); deviceList.addView(card);
        }
    }
    private final ScanCallback scanCallback = new ScanCallback() {
        @Override public void onScanResult(int callbackType, ScanResult result) { runOnUiThread(() -> { String key=result.getDevice().getAddress(); found.put(key,result.getDevice()); scanResults.put(key,result); renderDevices(); }); }
        @Override public void onBatchScanResults(java.util.List<ScanResult> results) { runOnUiThread(() -> { for(ScanResult result:results){String key=result.getDevice().getAddress();found.put(key,result.getDevice());scanResults.put(key,result);} renderDevices(); }); }
        @Override public void onScanFailed(int errorCode){runOnUiThread(()->{scanning=false;handler.removeCallbacks(stopScanTask);status.setText("BLE scan failed · code "+errorCode); addLog("SCAN_ERROR","","",String.valueOf(errorCode));toast("BLE scan failed (code "+errorCode+"). Toggle Bluetooth and retry.");});}
    };
    private void stopScan() {
        handler.removeCallbacks(stopScanTask);
        if(scanner!=null && scanning){try{scanner.stopScan(scanCallback);}catch(Exception ignored){} scanning=false; addLog("SCAN_STOP","","","stopped; devices="+scanResults.size()); if(gatt==null) status.setText(scanResults.isEmpty() && bondedDevices.isEmpty()?"No BLE devices found · retry with buds case open":"Scan stopped · select a device");}
    }
    private void connect(BluetoothDevice device,String name) {
        stopScan();
        if(!hasBtPermissions()){pendingScan=false;requestBtPermissions();toast("Allow Nearby devices permission, then connect again.");return;}
        try {
            if(gatt!=null){try{gatt.disconnect();}catch(Exception ignored){}gatt.close();gatt=null;}
            connectedName=name; status.setText("Connecting over BLE GATT to "+name+"…"); addLog("CONNECT","","",name+" address="+device.getAddress());
            gatt=device.connectGatt(this,false,gattCallback,BluetoothDevice.TRANSPORT_LE);
            if(gatt==null){status.setText("Could not start GATT connection");addLog("CONNECT_ERROR","","","connectGatt returned null");}
        } catch(Exception e){status.setText("Connect failed");addLog("CONNECT_ERROR","","",e.toString());toast("Connect failed: "+e.getMessage());}
    }
'''
s = s[:start] + replacement + s[end:]
old = 'if(newState==BluetoothProfile.STATE_CONNECTED){status.setText("GATT connected · "+connectedName+" · discovering services"); addLog("CONNECTED","","","GATT connected"); g.discoverServices();} else if(newState==BluetoothProfile.STATE_DISCONNECTED){status.setText("Disconnected"); addLog("DISCONNECTED","","","status="+statusCode); servicesBox.removeAllViews(); chars.clear(); g.close(); if(gatt==g)gatt=null;}'
new = 'if(newState==BluetoothProfile.STATE_CONNECTED){status.setText("GATT connected · "+connectedName+" · discovering services"); addLog("CONNECTED","","","GATT connected; status="+statusCode); boolean queued=g.discoverServices(); addLog("DISCOVER_SERVICES_REQUEST","","","queued="+queued);} else if(newState==BluetoothProfile.STATE_DISCONNECTED){status.setText("Disconnected · GATT status "+statusCode+" (buds may be busy/out of range)"); addLog("DISCONNECTED","","","status="+statusCode+" name="+connectedName); servicesBox.removeAllViews(); chars.clear(); g.close(); if(gatt==g)gatt=null;}'
if old not in s:
    raise SystemExit("Could not find expected GATT callback text; refusing to create partial patch")
s = s.replace(old,new)
source.write_text(s, encoding="utf-8")
print("Applied OnePlus Buds BLE discovery/connect patch")
