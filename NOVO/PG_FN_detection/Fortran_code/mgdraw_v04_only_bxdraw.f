*$ CREATE MGDRAW.FOR
*COPY MGDRAW
*                                                                      *
*=== mgdraw ===========================================================*
*                                                                      *
      SUBROUTINE MGDRAW ( ICODE, MREG )

*****************ADDED BY SANDER****************************************
* From my experience saving the file here reduces the simulation time  *
* by about half. (It only opens once, not for every bxdraw entry)      *
*      CHARACTER(LEN=50) :: Folder_path
*      Folder_path = '/media/sf_Delt_mappe/'
*      CHARACTER(LEN=75) :: File_path
*      SAVE
***************END ADDED BY SANDER**************************************

      INCLUDE '(DBLPRC)'
      INCLUDE '(DIMPAR)'
      INCLUDE '(IOUNIT)'
*
*----------------------------------------------------------------------*
*                                                                      *
*     Copyright (C) 1990-2013      by        Alfredo Ferrari           *
*     All Rights Reserved.                                             *
*                                                                      *
*                                                                      *
*     MaGnetic field trajectory DRAWing: actually this entry manages   *
*                                        all trajectory dumping for    *
*                                        drawing                       *
*                                                                      *
*     Created on   01 March 1990   by        Alfredo Ferrari           *
*                                              INFN - Milan            *
*     Last change   12-Nov-13      by        Alfredo Ferrari           *
*                                              INFN - Milan            *
*                                                                      *
*----------------------------------------------------------------------*
*
      INCLUDE '(CASLIM)'
      INCLUDE '(COMPUT)'
      INCLUDE '(SOURCM)'
      INCLUDE '(FHEAVY)'
      INCLUDE '(FLKSTK)'
      INCLUDE '(GENSTK)'
      INCLUDE '(MGDDCM)'
      INCLUDE '(PAPROP)'
      INCLUDE '(QUEMGD)'
      INCLUDE '(SUMCOU)'
      INCLUDE '(TRACKR)'
      INCLUDE '(RESNUC)' 
      INCLUDE '(EVTFLG)'

      INTEGER TrackID
* RESNUC added by Anna   

      DIMENSION DTQUEN ( MXTRCK, MAXQMG )
*
      CHARACTER*20 FILNAM
      LOGICAL LFCOPE
      SAVE LFCOPE
      DATA LFCOPE / .FALSE. /
*
*----------------------------------------------------------------------*
*                                                                      *
*     Icode = 1: call from Kaskad                                      *
*     Icode = 2: call from Emfsco                                      *
*     Icode = 3: call from Kasneu                                      *
*     Icode = 4: call from Kashea                                      *
*     Icode = 5: call from Kasoph                                      *
*                                                                      *
*----------------------------------------------------------------------*
*                                                                      *
      IF ( .NOT. LFCOPE ) THEN
         LFCOPE = .TRUE.
         IF ( KOMPUT .EQ. 2 ) THEN
            FILNAM = '/'//CFDRAW(1:8)//' DUMP A'
         ELSE
            FILNAM = CFDRAW
         END IF
         OPEN ( UNIT = IODRAW, FILE = FILNAM, STATUS = 'NEW', FORM =
     &          'UNFORMATTED' )

         OPEN(UNIT=89, FILE = 'parts_leaving_target.txt', 
     &    STATUS='UNKNOWN')
         OPEN(UNIT=90, FILE = 'scintillator_regions.txt', 
     &    STATUS='UNKNOWN')

      END IF
*  +-------------------------------------------------------------------*
*  |  Quenching is activated
      IF ( LQEMGD ) THEN
         IF ( MTRACK .GT. 0 ) THEN
            RULLL  = ZERZER
            CALL QUENMG ( ICODE, MREG, RULLL, DTQUEN )
*            WRITE (IODRAW) ( ( SNGL (DTQUEN (I,JBK)), I = 1, MTRACK ),
*     &                         JBK = 1, NQEMGD )
         END IF
      END IF
*  |  End of quenching
*     +-------------------------------------------------------------------*
      RETURN
*
*======================================================================*
*                                                                      *
*     Boundary-(X)crossing DRAWing:                                    *
*                                                                      *
*     Icode = 1x: call from Kaskad                                     *
*             19: boundary crossing                                    *
*     Icode = 2x: call from Emfsco                                     *
*             29: boundary crossing                                    *
*     Icode = 3x: call from Kasneu                                     *
*             39: boundary crossing                                    *
*     Icode = 4x: call from Kashea                                     *
*             49: boundary crossing                                    *
*     Icode = 5x: call from Kasoph                                     *
*             59: boundary crossing                                    *
*                                                                      *
*======================================================================*

****************END OF CODE BY ANNA****************************

      ENTRY BXDRAW ( ICODE, MREG, NEWREG, XSCO, YSCO, ZSCO )
***********************START BXDRAW CODE BY SANDER *********************
      
*      File_path = trim(Folder_path)//'testing/parts_leaving_target.txt'
*      OPEN(UNIT=89, FILE = '/media/sf_Delt_mappe/dump/'//
*     &    'parts_leaving_target.txt', STATUS='UNKNOWN')

*      File_path = trim(Folder_path)//'scintillator_regions.txt'
*      OPEN(UNIT=90, FILE = '/media/sf_Delt_mappe/dump/'//
*     &    'scintillator_regions.txt' , STATUS='UNKNOWN')  

* If particle is a photon (JTRACK = 7) and its previous interaction code is 101 or 106
* Then it is a prompt gamma (scattered prompt gammas are not prompt gammas)
* This definition implies that an alpha can travel and interact before sending out
* out a photon, and this photon will also be defined as a prompt gamma.
*
* If the particle is a neutron (JTRACK = 8) and its previoud interaction 
* code is 101, and its kinetic energy is above 100 keV, then it is a fast neutron
*
*     If any particle enters the scintillator bars (Region 1 - 48)
      IF (NEWREG .GE. 1 .AND. NEWREG .LE. 48) THEN
       IF (JTRACK .EQ. 7 .OR. JTRACK .EQ. 8) THEN
*       Write output about particles entering any scintillator region
        WRITE(90, '(1I7,1X,4I4,1X,5F13.6)')
     &      NCASE, JTRACK, MREG,
     &      NEWREG, LTRACK, ETRACK-AM(JTRACK),
     &      XSCO, YSCO, ZSCO, ATRACK*1E6
       END IF
*
      ELSE IF (NEWREG .EQ. 55 .AND. MREG .EQ. 49) THEN
       IF (JTRACK .EQ. 7 .OR. JTRACK .EQ. 8) THEN
*       Write output about particles exiting the target region
        WRITE(89, '(1I7,1X,4I4,1X,5F13.6)')
     &      NCASE, JTRACK, MREG,
     &      NEWREG, LTRACK, ETRACK-AM(JTRACK),
     &      XSCO, YSCO, ZSCO, ATRACK*1E6
       END IF
      END IF
*
****************END BXDRAW CODE BY SANDER*********************
      RETURN
      CLOSE(89)
      CLOSE(90)
*======================================================================*
*                                                                      *
*     Event End DRAWing:                                               *
*                                                                      *
*======================================================================*
*                                                                      *
      ENTRY EEDRAW ( ICODE )
      RETURN
*
*======================================================================*
*                                                                      *
*     ENergy deposition DRAWing:                                       *
*                                                                      *
*     Icode = 1x: call from Kaskad                                     *
*             10: elastic interaction recoil                           *
*             11: inelastic interaction recoil                         *
*             12: stopping particle                                    *
*             13: pseudo-neutron deposition                            *
*             14: escape                                               *
*             15: time kill                                            *
*     Icode = 2x: call from Emfsco                                     *
*             20: local energy deposition (i.e. photoelectric)         *
*             21: below threshold, iarg=1                              *
*             22: below threshold, iarg=2                              *
*             23: escape                                               *
*             24: time kill                                            *
*     Icode = 3x: call from Kasneu                                     *
*             30: target recoil                                        *
*             31: below threshold                                      *
*             32: escape                                               *
*             33: time kill                                            *
*     Icode = 4x: call from Kashea                                     *
*             40: escape                                               *
*             41: time kill                                            *
*             42: delta ray stack overflow                             *
*     Icode = 5x: call from Kasoph                                     *
*             50: optical photon absorption                            *
*             51: escape                                               *
*             52: time kill                                            *
*                                                                      *
*======================================================================*
*                                                                      *
      ENTRY ENDRAW ( ICODE, MREG, RULL, XSCO, YSCO, ZSCO )

      IF ( .NOT. LFCOPE ) THEN
         LFCOPE = .TRUE.
         IF ( KOMPUT .EQ. 2 ) THEN
            FILNAM = '/'//CFDRAW(1:8)//' DUMP A'
         ELSE
            FILNAM = CFDRAW
         END IF
         OPEN ( UNIT = IODRAW, FILE = FILNAM, STATUS = 'NEW', FORM =
     &          'UNFORMATTED' )
      END IF
*      WRITE (IODRAW)  0, ICODE, JTRACK, SNGL (ETRACK), SNGL (WTRACK)
*      WRITE (IODRAW)  SNGL (XSCO), SNGL (YSCO), SNGL (ZSCO), SNGL (RULL)
*  +-------------------------------------------------------------------*
*  |  Quenching is activated : calculate quenching factor
*  |  and store quenched energy in DTQUEN(1, jbk)
      IF ( LQEMGD ) THEN
         RULLL = RULL
         CALL QUENMG ( ICODE, MREG, RULLL, DTQUEN )
*         WRITE (IODRAW) ( SNGL (DTQUEN(1, JBK)), JBK = 1, NQEMGD )
      END IF
*  |  end quenching
*  +-------------------------------------------------------------------*
      RETURN
*
*======================================================================*
*                                                                      *
*     SOurce particle DRAWing:                                         *
*                                                                      *
*======================================================================*
*
      ENTRY SODRAW
      IF ( .NOT. LFCOPE ) THEN

      END IF
*      WRITE (IODRAW) -NCASE, NPFLKA, NSTMAX, SNGL (TKESUM),
*     &                SNGL (WEIPRI)
*  +-------------------------------------------------------------------*
*  |  (Radioactive) isotope: it works only for 1 source particle on
*  |  the stack for the time being
      IF ( ILOFLK (NPFLKA) .GE. 100000 .AND. LRADDC (NPFLKA) ) THEN
         IARES  = MOD ( ILOFLK (NPFLKA), 100000  )  / 100
         IZRES  = MOD ( ILOFLK (NPFLKA), 10000000 ) / 100000
         IISRES = ILOFLK (NPFLKA) / 10000000
         IONID  = ILOFLK (NPFLKA)
*         WRITE (IODRAW) ( IONID,SNGL(-TKEFLK(I)),
*     &                    SNGL (WTFLK(I)), SNGL (XFLK (I)),
*     &                    SNGL (YFLK (I)), SNGL (ZFLK (I)),
*     &                    SNGL (TXFLK(I)), SNGL (TYFLK(I)),
*     &                    SNGL (TZFLK(I)), I = 1, NPFLKA )
*  |
*  +-------------------------------------------------------------------*
*  |  Patch for heavy ions: it works only for 1 source particle on
*  |  the stack for the time being
      ELSE IF ( ABS (ILOFLK (NPFLKA)) .GE. 10000 ) THEN
         IONID = ILOFLK (NPFLKA)
         CALL DCDION ( IONID )
*  |
*  +-------------------------------------------------------------------*
*  |  Patch for heavy ions: ???
      ELSE IF ( ILOFLK (NPFLKA) .LT. -6 ) THEN
*         WRITE (IODRAW) ( IONID,SNGL(TKEFLK(I)+AMNHEA(-ILOFLK(NPFLKA))),
*     &                    SNGL (WTFLK(I)), SNGL (XFLK (I)),
*     &                    SNGL (YFLK (I)), SNGL (ZFLK (I)),
*     &                    SNGL (TXFLK(I)), SNGL (TYFLK(I)),
*     &                    SNGL (TZFLK(I)), I = 1, NPFLKA )
*  |
*  +-------------------------------------------------------------------*
*  |
      ELSE
*         WRITE (IODRAW) ( ILOFLK(I), SNGL (TKEFLK(I)+AM(ILOFLK(I))),
*     &                    SNGL (WTFLK(I)), SNGL (XFLK (I)),
*     &                    SNGL (YFLK (I)), SNGL (ZFLK (I)),
*     &                    SNGL (TXFLK(I)), SNGL (TYFLK(I)),
*     &                    SNGL (TZFLK(I)), I = 1, NPFLKA )
      END IF
*  |
*  +-------------------------------------------------------------------*
      RETURN
*
*======================================================================*
*                                                                      *
*     USer dependent DRAWing:                                          *
*                                                                      *
*     Icode = 10x: call from Kaskad                                    *
*             100: elastic   interaction secondaries                   *
*             101: inelastic interaction secondaries                   *
*             102: particle decay  secondaries                         *
*             103: delta ray  generation secondaries                   *
*             104: pair production secondaries                         *
*             105: bremsstrahlung  secondaries                         *
*             110: decay products                                      *
*     Icode = 20x: call from Emfsco                                    *
*             208: bremsstrahlung secondaries                          *
*             210: Moller secondaries                                  *
*             212: Bhabha secondaries                                  *
*             214: in-flight annihilation secondaries                  *
*             215: annihilation at rest   secondaries                  *
*             217: pair production        secondaries                  *
*             219: Compton scattering     secondaries                  *
*             221: photoelectric          secondaries                  *
*             225: Rayleigh scattering    secondaries                  *
*             237: mu pair     production secondaries                  *
*     Icode = 30x: call from Kasneu                                    *
*             300: interaction secondaries                             *
*     Icode = 40x: call from Kashea                                    *
*             400: delta ray  generation secondaries                   *
*  For all interactions secondaries are put on GENSTK common (kp=1,np) *
*  but for KASHEA delta ray generation where only the secondary elec-  *
*  tron is present and stacked on FLKSTK common for kp=npflka          *
*                                                                      *
*======================================================================*
      ENTRY USDRAW ( ICODE, MREG, XSCO, YSCO, ZSCO )

* ****Parameter definitions****                                        *
*                                                                      *
* ICODE = interaction code. Important icodes are 101 for inelastic     *
* interaction, 100 for elastic interaction, 106 for de-excitation, 300 *
* for low energy neutron interaction                                   *
*
* NCASE = history number. For number of primaries = 1000, NCASE will   *
* range from 1 to 1000                                                 *
*
* MREG = current region. Regions values in current NOVO detector model:*
*   1 - 48: Scintillator bars                                          *
*       49: PMMA target                                                *
*       50: Void amongst the scintillator bars                         *
*  51 - 54: Void amongst the electronic boxes                          *
*       55: Void outside the detector                                  *
*       56: Blackbody                                                  *
* 57 - 152: Electric boxes at the ends of each bars                    *
* 153 -200: Voids inside electric boxes
*
* JTRACK = id of the current particle being tracked. If jtrack = 1 it  *
* means that the particle that is being tracked is a proton.           *
* The combination JTRACK.EQ.1 and ICODE.EQ.101 means the current       *       
* interaction was inelastic and caused by a proton.    
*
* NP = Number of secondaries. This is specific to the FLUKA stack 
* called GENSTK, which is the stack where secondary particles are being*
* saved. However, information about the residual nucleus is not saved  * 
* in this stack, but in the FLUKA stack named FHEAVY. If one wishes to *
* loop over FHEAVY, one should use NPHEAV instead of NP. See FHEAVY and* 
* GENSTK files for further information.                                *

* Tki(IP) = kinetic energy of the IPth secondary.                      *
* XSCO,YSCO,ZSCO = X,Y,Z coordinate of the interaction                 * 
* Cxr(IP),Cyr(IP),Czr(IP) = x,y,z cosines of the angle the IPth        * 
* particle was emitted with.                                           *


*Use ISPUSR for saving integer values: ICODE, NCASE, JTRACK
*USE SPAUSR for saving floats

      IF ( .NOT. LFCOPE ) THEN
         LFCOPE = .TRUE.
         IF ( KOMPUT .EQ. 2 ) THEN
            FILNAM = '/'//CFDRAW(1:8)//' DUMP A'
         ELSE
            FILNAM = CFDRAW
         END IF
         OPEN ( UNIT = IODRAW, FILE = FILNAM, STATUS = 'NEW', FORM =
     &          'UNFORMATTED' )
      END IF
* No output by default:
      RETURN

*=== End of subrutine Mgdraw ==========================================*    
      END
      
