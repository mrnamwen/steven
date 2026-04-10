#include "StevenApp.h"
#include <NiMain.h>
#include <NiStream.h>
#include <NiAnimation.h>
#include <NiParticle.h>
#include <NiCollision.h>
#include <stdio.h>

//---------------------------------------------------------------------------
NiApplication* NiApplication::Create()
{
    return NiNew StevenApp;
}
//---------------------------------------------------------------------------
StevenApp::StevenApp()
    : NiApplication("Steven - SMT:Imagine Client", 1280, 720, false)
    , m_kCamPos(0.0f, 50.0f, 0.0f)
    , m_fCamYaw(0.0f)
    , m_fCamPitch(0.0f)
    , m_fMoveSpeed(100.0f)
    , m_fLookSpeed(2.0f)
{
    // Use absolute path — relative paths don't always resolve under Wine
    SetMediaPath("assets\\zones\\");
}
//---------------------------------------------------------------------------
bool StevenApp::Initialize()
{
    if (!NiApplication::Initialize())
        return false;

    return true;
}
//---------------------------------------------------------------------------
bool StevenApp::LoadZoneNIF(const char* pcFilename)
{
    NiStream kStream;

    const char* pcConverted = NiApplication::ConvertMediaFilename(pcFilename);

    FILE* pLog = fopen("steven.log", "a");
    if (pLog)
    {
        fprintf(pLog, "Loading: '%s' (converted: '%s')\n", pcFilename, pcConverted);

        // Raw file open test
        FILE* pTest = fopen(pcConverted, "rb");
        if (pTest)
        {
            fseek(pTest, 0, SEEK_END);
            long sz = ftell(pTest);
            fseek(pTest, 0, SEEK_SET);
            char header[64];
            memset(header, 0, sizeof(header));
            fread(header, 1, 60, pTest);
            fclose(pTest);
            fprintf(pLog, "  File exists: %ld bytes, header: '%.40s'\n", sz, header);
        }
        else
        {
            fprintf(pLog, "  fopen FAILED for '%s'\n", pcConverted);
            // Try with forward slashes
            char szAlt[256];
            strncpy(szAlt, pcConverted, 255);
            for (char* p = szAlt; *p; p++) { if (*p == '\\') *p = '/'; }
            pTest = fopen(szAlt, "rb");
            fprintf(pLog, "  fopen with '/' for '%s': %s\n", szAlt,
                pTest ? "OK" : "FAILED");
            if (pTest) fclose(pTest);
        }
        fflush(pLog);
    }

    bool bSuccess = kStream.Load(pcConverted);

    if (!bSuccess)
    {
        if (pLog)
        {
            fprintf(pLog, "  NiStream error code: %d\n", kStream.GetLastError());
            fprintf(pLog, "  NiStream error msg: %s\n", kStream.GetLastErrorMessage());
            fclose(pLog);
        }
        return false;
    }

    unsigned int uiObjects = kStream.GetObjectCount();
    if (pLog) fprintf(pLog, "  Loaded %d objects\n", uiObjects);

    int iAttached = 0;
    for (unsigned int i = 0; i < uiObjects; i++)
    {
        NiObject* pkObj = kStream.GetObjectAt(i);
        if (pkObj)
        {
            if (pLog)
            {
                const NiRTTI* pkRTTI = pkObj->GetRTTI();
                fprintf(pLog, "  Object[%d]: %s\n", i,
                    pkRTTI ? pkRTTI->GetName() : "unknown");
            }

            if (NiIsKindOf(NiNode, pkObj))
            {
                m_spScene->AttachChild((NiNode*)pkObj);
                iAttached++;
            }
        }
    }

    if (pLog)
    {
        fprintf(pLog, "  Attached %d nodes to scene\n", iAttached);
        fclose(pLog);
    }

    m_spScene->Update(0.0f);
    m_spScene->UpdateProperties();

    return iAttached > 0;
}
//---------------------------------------------------------------------------
bool StevenApp::CreateScene()
{
    // Alpha accumulator for proper transparency sorting
    NiAlphaAccumulator* pkAccum = NiNew NiAlphaAccumulator;
    m_spRenderer->SetSorter(pkAccum);

    m_spScene = NiNew NiNode;

    // Try to load zone NIFs - try several in order
    const char* zones[] = {
        "ClientDebugMap.nif",
        "MA01_001_01.nif",
        "MB01_001_01.nif",
        NULL
    };

    bool bLoaded = false;
    for (int i = 0; zones[i] != NULL; i++)
    {
        if (LoadZoneNIF(zones[i]))
        {
            bLoaded = true;
            break;
        }
    }

    if (!bLoaded)
    {
        NiOutputDebugString("No zone NIF found. Running with empty scene.\n");
    }

    m_spScene->UpdateEffects();
    m_spScene->Update(0.0f);

    return true;
}
//---------------------------------------------------------------------------
bool StevenApp::CreateCamera()
{
    m_spCamera = NiNew NiCamera;

    NiFrustum kFrustum;
    kFrustum.m_fLeft   = -0.5f;
    kFrustum.m_fRight  =  0.5f;
    kFrustum.m_fTop    =  0.5f;
    kFrustum.m_fBottom = -0.5f;
    kFrustum.m_fNear   =  1.0f;
    kFrustum.m_fFar    = 50000.0f;
    m_spCamera->SetViewFrustum(kFrustum);

    float fAspect = (float)m_pkAppWindow->GetWidth() /
                    (float)m_pkAppWindow->GetHeight();
    m_spCamera->AdjustAspectRatio(fAspect);

    m_spCamera->SetTranslate(m_kCamPos);
    m_spCamera->Update(0.0f);

    return true;
}
//---------------------------------------------------------------------------
void StevenApp::ProcessInput()
{
    NiApplication::ProcessInput();

    NiInputKeyboard* pkKeyboard = GetInputSystem()->GetKeyboard();
    if (!pkKeyboard)
        return;

    float dt = GetFrameTime();
    if (dt <= 0.0f || dt > 0.5f)
        dt = 0.016f;

    // Mouse look (right mouse button or always)
    NiInputMouse* pkMouse = GetInputSystem()->GetMouse();
    if (pkMouse)
    {
        int iDX = 0, iDY = 0;
        pkMouse->GetPositionDelta(iDX, iDY);

        if (pkMouse->ButtonIsDown(NiInputMouse::NIM_RIGHT))
        {
            m_fCamYaw   -= (float)iDX * m_fLookSpeed * 0.003f;
            m_fCamPitch -= (float)iDY * m_fLookSpeed * 0.003f;
        }
    }

    // Arrow keys also rotate
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_LEFT))
        m_fCamYaw += m_fLookSpeed * dt;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_RIGHT))
        m_fCamYaw -= m_fLookSpeed * dt;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_UP))
        m_fCamPitch += m_fLookSpeed * dt;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_DOWN))
        m_fCamPitch -= m_fLookSpeed * dt;

    // Clamp pitch
    if (m_fCamPitch >  1.4f) m_fCamPitch =  1.4f;
    if (m_fCamPitch < -1.4f) m_fCamPitch = -1.4f;

    // Calculate forward/right vectors from yaw/pitch
    float fCosP = NiCos(m_fCamPitch);
    NiPoint3 kForward(
        fCosP * NiSin(m_fCamYaw),
        NiSin(m_fCamPitch),
        fCosP * NiCos(m_fCamYaw)
    );
    NiPoint3 kRight(
        NiCos(m_fCamYaw),
        0.0f,
        -NiSin(m_fCamYaw)
    );
    NiPoint3 kUp(0.0f, 1.0f, 0.0f);

    float fSpeed = m_fMoveSpeed;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_LSHIFT))
        fSpeed *= 5.0f;

    // WASD movement
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_W))
        m_kCamPos += kForward * fSpeed * dt;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_S))
        m_kCamPos -= kForward * fSpeed * dt;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_A))
        m_kCamPos -= kRight * fSpeed * dt;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_D))
        m_kCamPos += kRight * fSpeed * dt;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_SPACE))
        m_kCamPos += kUp * fSpeed * dt;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_LCONTROL))
        m_kCamPos -= kUp * fSpeed * dt;
}
//---------------------------------------------------------------------------
void StevenApp::UpdateFrame()
{
    // Update camera transform from fly-camera state
    float fCosP = NiCos(m_fCamPitch);
    NiPoint3 kForward(
        fCosP * NiSin(m_fCamYaw),
        NiSin(m_fCamPitch),
        fCosP * NiCos(m_fCamYaw)
    );

    m_spCamera->SetTranslate(m_kCamPos);
    m_spCamera->LookAtWorldPoint(
        m_kCamPos + kForward,
        NiPoint3(0.0f, 1.0f, 0.0f));
    m_spCamera->Update(m_fAccumTime);

    NiApplication::UpdateFrame();
}
//---------------------------------------------------------------------------
