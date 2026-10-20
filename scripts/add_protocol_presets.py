from pathlib import Path
p=Path("BudsyProtocolLab/app/src/main/java/com/budsy/protocollab/MainActivity.java")
s=p.read_text(encoding="utf-8")
if "buildProtocolCommands();" in s:
    print("protocol presets already added")
    raise SystemExit(0)
s=s.replace("private LinearLayout root, content, deviceList, servicesBox, logBox;", "private LinearLayout root, content, deviceList, servicesBox, protocolBox, logBox;")
s=s.replace('section("GATT services & characteristics"); servicesBox = new LinearLayout(this); servicesBox.setOrientation(LinearLayout.VERTICAL); root.addView(servicesBox);', 'section("GATT services & characteristics"); servicesBox = new LinearLayout(this); servicesBox.setOrientation(LinearLayout.VERTICAL); root.addView(servicesBox); section("Observed protocol commands"); protocolBox = new LinearLayout(this); protocolBox.setOrientation(LinearLayout.VERTICAL); root.addView(protocolBox); buildProtocolCommands();')
marker="    private boolean hasBtPermissions() {"
methods=r'''    private void buildProtocolCommands() {
        protocolBox.addView(text("Frames copied from your capture. Meanings are not fully verified. Connect first; choose a writable characteristic and confirm each send.",12,muted));
        String[][] p={{"State A","01 0C 01 01"},{"State B","01 0C 02 01"},{"Feature list","01 08 02 03 01"},{"Value list","01 0D 07 06 05 0B 11 1B 1D 20"},{"Query 010F","01 0F"},{"Query 0124","01 24"},{"Query 0105","01 05"},{"Query 0109","01 09"},{"Profiles","01 22"},{"Device info","01 12"},{"Observed 0106","01 06"}};
        for(int i=0;i<p.length;i+=2){LinearLayout r=row();final String a=p[i][0],b=p[i][1];addButton(r,a,()->chooseProtocolTarget(a,b));if(i+1<p.length){final String c=p[i+1][0],d=p[i+1][1];addButton(r,c,()->chooseProtocolTarget(c,d));}protocolBox.addView(r);}
    }
    private void chooseProtocolTarget(String label,String payload) {
        if(gatt==null){toast("Connect and discover GATT services first.");return;}
        ArrayList<BluetoothGattCharacteristic> list=new ArrayList<>();ArrayList<String> names=new ArrayList<>();
        for(BluetoothGattCharacteristic c:chars.values()){int q=c.getProperties();if((q&(BluetoothGattCharacteristic.PROPERTY_WRITE|BluetoothGattCharacteristic.PROPERTY_WRITE_NO_RESPONSE))!=0){list.add(c);names.add(c.getUuid()+" · "+properties(q));}}
        if(list.isEmpty()){toast("No writable GATT characteristic found.");return;}
        new AlertDialog.Builder(this).setTitle("Choose target for "+label).setItems(names.toArray(new String[0]),(d,n)->new AlertDialog.Builder(this).setTitle("Confirm protocol frame").setMessage(payload+"\n\nMeaning is not verified. Send only to your own device.").setNegativeButton("Cancel",null).setPositiveButton("Send",(x,y)->writeProtocolTarget(list.get(n),payload,label)).show()).setNegativeButton("Cancel",null).show();
    }
    private void writeProtocolTarget(BluetoothGattCharacteristic c,String payload,String label) {
        try{String[] p=payload.split("\\s+");byte[] b=new byte[p.length];for(int i=0;i<p.length;i++)b[i]=(byte)Integer.parseInt(p[i],16);int t=(c.getProperties()&BluetoothGattCharacteristic.PROPERTY_WRITE)!=0?BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT:BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE;boolean ok;if(Build.VERSION.SDK_INT>=33)ok=gatt.writeCharacteristic(c,b,t)==BluetoothStatusCodes.SUCCESS;else{c.setWriteType(t);c.setValue(b);ok=gatt.writeCharacteristic(c);}addLog("PROTOCOL_TX",serviceUuid(c),c.getUuid().toString(),label+" HEX="+hex(b)+" queued="+ok);if(!ok)toast("Write not queued.");}catch(Exception e){addLog("PROTOCOL_TX_ERROR",serviceUuid(c),c.getUuid().toString(),e.toString());toast("Send failed: "+e.getMessage());}
    }
'''
if marker not in s: raise SystemExit("method insertion point missing")
s=s.replace(marker,methods+marker)
p.write_text(s,encoding="utf-8")
g=Path("BudsyProtocolLab/app/build.gradle")
t=g.read_text(encoding="utf-8").replace("versionCode 2","versionCode 3").replace("versionName '0.2.0'","versionName '0.3.0'")
g.write_text(t,encoding="utf-8")
print("Protocol presets added")
