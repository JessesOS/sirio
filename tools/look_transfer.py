"""Transfer the lighting and colour of an AI-relit clip onto the real footage, at partial strength.

The relit clip only supplies a smooth per-pixel gain (how much brighter/warmer each area became).
That gain is applied to the original pixels, so the real face, lip sync and resolution are kept.

usage: look_transfer.py original.mp4 relit.mp4 out.mp4 [strength=0.5] [face_lift=0.25]
"""
import sys,subprocess
import av,cv2,numpy as np
src,relit,out=sys.argv[1:4]
strength=float(sys.argv[4]) if len(sys.argv)>4 else 0.5
face_lift=float(sys.argv[5]) if len(sys.argv)>5 else 0.25
PW=480  # working width for the gain maps
def lin(x):return np.power(x.astype(np.float32)/255.0,2.2)
def frames(path):
    with av.open(path) as c:
        s=c.streams.video[0]
        for f in c.decode(video=0):yield float(f.pts*s.time_base),f.to_ndarray(format='bgr24')
relit_frames=list(frames(relit))
rt=np.array([t for t,_ in relit_frames])
with av.open(src) as c:
    s=c.streams.video[0];W,H,fps=s.width,s.height,float(s.average_rate)
PH=int(round(PW*H/W))
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-i',src,'-map','0:v','-map','1:a?','-c:v','libx264','-crf','14','-preset','slow','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',out],stdin=subprocess.PIPE)
face=None
yy,xx=np.mgrid[0:PH,0:PW].astype(np.float32)
for t,frame in frames(src):
    r=relit_frames[int(np.abs(rt-t).argmin())][1]
    a=lin(cv2.resize(frame,(PW,PH),interpolation=cv2.INTER_AREA));b=lin(cv2.resize(r,(PW,PH),interpolation=cv2.INTER_AREA))
    # face position (smoothed) -> soft mask
    # the face is taken as the largest skin-coloured area in the upper half (seated interview framing)
    ycc=cv2.cvtColor(cv2.resize(frame,(PW,PH),interpolation=cv2.INTER_AREA),cv2.COLOR_BGR2YCrCb)
    skin=((ycc[...,1]>138)&(ycc[...,1]<175)&(ycc[...,2]>95)&(ycc[...,2]<130)&(ycc[...,0]>40)).astype(np.uint8)
    skin[int(PH*0.5):]=0;skin=cv2.morphologyEx(skin,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,_,st,_=cv2.connectedComponentsWithStats(skin)
    if n>1:
        # prefer the blob near the horizontal centre, so warm props (wood, bamboo) are not mistaken for the face
        cxs=st[1:,0]+st[1:,2]/2;score=st[1:,cv2.CC_STAT_AREA]*np.exp(-((cxs-PW/2)/(PW*0.12))**2)
        k=1+int(score.argmax());x,y,w,h=st[k,:4]
        if st[k,cv2.CC_STAT_AREA]>PW*PH*0.004:
            cur=np.array([x+w/2,y+h/2,w,h],np.float32)
            face=cur if face is None else face*0.8+cur*0.2
    fm=np.zeros((PH,PW),np.float32)
    if face is not None:
        cx,cy,w,h=face;fm=np.clip(1.6-np.sqrt(((xx-cx)/(w*0.62))**2+((yy-cy)/(h*0.80))**2)*1.6,0,1)
        fm=cv2.GaussianBlur(fm,(0,0),w*0.12)
    def gain(sig):
        return (cv2.GaussianBlur(b,(0,0),sig)+0.004)/(cv2.GaussianBlur(a,(0,0),sig)+0.004)
    # fine gain keeps thin rim lights and edges; a broad gain on the face avoids ghosting the mouth
    G=gain(PW*0.012)*(1-fm[...,None])+gain(PW*0.05)*fm[...,None]
    G=np.clip(G,0.2,5.0)**strength
    # never let the relight darken the face: floor its brightness gain at 1 inside the face mask
    lum=G.mean(axis=2,keepdims=True);G=G*(1+fm[...,None]*(np.maximum(lum,1.0)/lum-1))
    G=cv2.resize(G,(W,H),interpolation=cv2.INTER_CUBIC)
    o=lin(frame)*G
    o=np.power(np.clip(o,0,1),1/2.2)
    if face_lift>0:
        m=cv2.resize(fm,(W,H),interpolation=cv2.INTER_CUBIC)[...,None]
        lifted=o+face_lift*o*(1-o)**2.2  # raises shadows and mids, leaves highlights
        o=o*(1-m)+lifted*m
    enc.stdin.write((np.clip(o,0,1)*255+0.5).astype(np.uint8).tobytes())
enc.stdin.close();enc.wait()
print('written',out)
